import streamlit as st 
from src.data_eng.DataRequest import Requests
import datetime as dt 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np 
import pandas as pd 
from src.analytics.PlotSurface import Plot3d
import os 
from src.analytics.MarkovChain import MarkovModel
import joblib
from sklearn.preprocessing import StandardScaler
#from analytics.ReturnPrices import hmm_
from src.analytics.ReturnPrices import returns_prices
from src.analytics.RiskBandsFunc import risk_bands_func
codes_list = ['24364']
start_date = "01/01/2003"
end_date = dt.date.today().strftime("%d/%m/%Y")
print(start_date)
print(end_date)

# fazendo requisiçao dos dados e pegando dataframe
req_data = Requests(codes_list)
data = req_data.get_data(start_date, end_date)
data = req_data.get_dataframe() #dataframe
#st.markdown('hello')

# pegando dados de PETR4 e IBOV no yfinance 
tickers = ['PETR4.SA']
yf_start_date = '2003-01-01'
yf_end_date = dt.date.today()
print(yf_end_date)
yf_data = req_data.y_finance_req(tickers, yf_start_date, yf_end_date)

# sinais do yahoo
petr4 = yf_data['Close_PETR4.SA']
ibov = req_data.get_ibov('^BVSP', yf_start_date, yf_end_date)
ibov_ = ibov['Close_IBOV']


# =========================================================================================
#           STREAMLIT
#=========================================================================================

st.markdown("""
            # Hey! 
            This is a solution to the problem of price volatility in oil scenarios in Brazil.
            Enjoy this application! 
            
            
            """)

fig_line = px.line(x=data.index, y=data['IBC-Br'])
fig_line.update_layout(xaxis_title='Time', title='IBC-Br - Historical', width=850, yaxis_title='IBC-Br')

fig_petr4 = go.Figure()
fig_petr4.add_trace(go.Scatter(x=petr4.index, y=petr4, mode='lines', name='PETR4', line=dict(color="#00D2C4", width=3)))
fig_petr4.update_layout(title= 'PETR4.SA - Historical', xaxis_title='Time', width=350)

fig_ibov = go.Figure()
fig_ibov.add_trace(go.Scatter(x=ibov_.index, y=ibov_, mode='lines', name='^IBOV', line=dict(color="#94A3B8", width=3)))
fig_ibov.update_layout(title='IBOVESPA - Historical', xaxis_title='Time', width=350)


# plotando grafico do IBC-Br 

st.plotly_chart(fig_line)

col1, col2 = st.columns(2, gap='large')
with col1:
    st.plotly_chart(fig_ibov)
    
with col2:
    st.plotly_chart(fig_petr4)
    

# calculando lados dos preços
worst_price = petr4.min()
best_price = petr4.max()
change_price_best = petr4.pct_change().max()
change_price_worst = ((worst_price - petr4.mean())/petr4.mean())*100
row = st.container(horizontal=True)
with row:
    st.metric("Monthly Price - PETR4.SA", np.round(best_price,2), np.round(change_price_best,2), border=True, chart_type='area', chart_data=petr4)
    
# calculando beta 
def BETA(petra:pd.Series, ibov:pd.Series): 
    data = pd.concat([petra, ibov], join='inner', axis=1).dropna()
    returns = data.pct_change()
    cov = returns['Close_PETR4.SA'].rolling(12).cov(returns['Close_IBOV'])
    var = returns['Close_IBOV'].rolling(12).var()
    data['BETA'] = cov/var
    return data.dropna()


st.markdown('# Formulation - Beta Index')
st.text("""The Beta index was used in this work as an indicator of the asset's sensitivity to the market.

The formula is the ratio between the covariance of the asset's return and the market's return, with the variance of the market.
        
        """)
df_with_beta = BETA(petr4, ibov_)
fig_beta = go.Figure()
fig_beta.add_trace(go.Scatter(x=df_with_beta.index, y=df_with_beta['BETA'], mode='lines', name='Beta', line=dict(color="#34D399", width=3)))
fig_beta.update_layout(title='BETA - Historical', xaxis_title='Time', yaxis_title='Beta')
st.plotly_chart(fig_beta)

# mostrando dataframe
df_with_beta['IBC-Br'] = data['IBC-Br']
st.dataframe(df_with_beta)

# calculando sigma (volatilidade)
def calculate_sigma(petr4:pd.Series):
    ret = np.log(petr4)/petr4.shift()
    return ret.rolling(3).std().shift(-3)

df_with_beta['Sigma'] = calculate_sigma(df_with_beta['Close_PETR4.SA'])

# plotando linhas do sigma 
fig_sigma = go.Figure()
fig_sigma.add_trace(go.Scatter(x=df_with_beta.index, y=df_with_beta['Sigma'], mode='lines', name='Beta', line=dict(color="#FC3636", width=3)))
fig_sigma.update_layout(title='PETR4.SA - Volatility', xaxis_title='Time', yaxis_title='Sigma')
st.plotly_chart(fig_sigma)

sigma_trend = df_with_beta['Sigma'].rolling(12).mean()
trend_sigma_fig = go.Figure()
trend_sigma_fig.add_trace(go.Scatter(x=sigma_trend.index, y=sigma_trend, mode='lines', name='Sigma', line=dict(color="#FC3636", width=3)))
trend_sigma_fig.update_layout(title='Trend - Volatility', xaxis_title='Time', yaxis_title='Sigma', )
st.plotly_chart(trend_sigma_fig)


# plotando area do sigma 
surface  = Plot3d(df_with_beta['IBC-Br'], df_with_beta['BETA'], df_with_beta['Sigma'], 'Area - Volatility by IBC-Br and Beta')
surface1 = surface.plot_surface()
st.plotly_chart(surface1)

# area de volatilidade por regime
df_with_beta['Regime'] = MarkovModel(df_with_beta)
df_with_beta['Regime'] = df_with_beta['Regime'].fillna(0)
st.dataframe(df_with_beta)

mask = df_with_beta['Regime'] == 0

# plotando regime pelo sigma 
fig_regime = go.Figure()
fig_regime.add_trace(go.Scatter(x=df_with_beta.index, y=df_with_beta['Sigma'], mode='lines',line=dict(width=2, color="#FC3636"), name='sigma'))
fig_regime.add_trace(go.Scatter(x=df_with_beta.index[mask], y=df_with_beta.loc[mask, 'Sigma'], mode='markers', marker=dict(size=8, color="#0CFF04", symbol='circle'), name='regime'))
fig_regime.update_layout(title='Volatility with regime marking',xaxis_title='Time',yaxis_title='Sigma',template='plotly_dark')
st.plotly_chart(fig_regime)

# plotando histograma do sigma e regime 
df_hist = df_with_beta.copy()
df_hist['Regime'].replace(0, 'Yes', inplace=True)
df_hist['Regime'].replace(1, 'No', inplace=True)
hist1 = px.histogram(df_hist, 'Sigma', color='Regime') 
hist1.update_layout(title='Distribution Sigma and Regime', yaxis_title='Frequency')
st.plotly_chart(hist1)

# plotando area de regime em 3d 
reg3d  = Plot3d(mask, df_with_beta['BETA'], df_with_beta['Sigma'], 'Volatility Area with Regime')
reg_3d_plot = reg3d.plot_surface()
st.plotly_chart(reg_3d_plot)

# produçao do petroleo 

petr4_prod = ['1389', '22707']
prod_req = Requests(petr4_prod)
data_prod = prod_req.get_data(start_date, end_date)
data_prod = prod_req.get_dataframe()

fig_prod = go.Figure()
fig_prod.add_trace(go.Scatter(x=data_prod.index, y=data_prod['Produção de derivados de petróleo'].rolling(12).mean(), mode='lines',line=dict(width=2, color="#0011ff"), name='Produção de Derivados do Petróleo'))
fig_prod.add_trace(go.Scatter(x=data_prod.index, y=data_prod['Balança comercial'].rolling(12).mean(), mode='lines', line=dict(width=2, color="#3bd27a"), name='Balança Comercial'))
fig_prod.update_layout(title='Production of Petroleum Derivatives and Trade Balance - Moving AVG')
st.plotly_chart(fig_prod, use_container_width=True)

# area de produçao de derivados, ibc-br e petr4 
fig_ibc_prod = Plot3d(data_prod['Produção de derivados de petróleo'][:len(df_with_beta)], df_with_beta['IBC-Br'], df_with_beta['Close_PETR4.SA'], 'PETR4 Dynamics Across Economic Activity and Oil Production')
st.plotly_chart(fig_ibc_prod.plot_surface())


# criando funçao para calculo de drawdown
def drawdown(data:pd.Series):
    max_rolling = data.cummax()
    return (data/max_rolling)-1

dd_petr4 = drawdown(petr4)
fig_dd_petr4 = px.area(dd_petr4)
fig_dd_petr4.update_layout(title='Drawdown - Close_PETR4.SA', yaxis_title='Drawdown')

#calculando dd para o ibov 
dd_ibov = drawdown(ibov_)
fig_dd_ibov = px.area(dd_ibov)
fig_dd_ibov.update_layout(title='Drawdown - IBOVESPA', yaxis_title='Drawdown')

dd_col1, dd_col2 = st.columns(2)
with dd_col1:
    st.plotly_chart(fig_dd_petr4)
    st.metric(label='Max Drawdown', value=round(dd_petr4.min(),2))
with dd_col2:
    st.plotly_chart(fig_dd_ibov)
    st.metric(label='Max Drawdown', value=round(dd_ibov.min(),2))

#plotando regime ao longo do historico de BETA
fig_beta_regime = px.line(df_with_beta['BETA'])
fig_beta_regime.add_trace(go.Scatter(x=df_with_beta.index,y=df_with_beta['Regime'], mode='lines', marker=dict(size=8, color="#FF6804", symbol='0'), name='regime'))
fig_beta_regime.add_trace(go.Scatter(x=df_with_beta.index,y=df_with_beta['Regime'], mode='markers', marker=dict(size=8, color="#FF6804", symbol='circle'), name='regime'))
fig_beta_regime.update_layout(title='Regime Transitions by BETA', xaxis_title='date', yaxis_title='BETA')
st.plotly_chart(fig_beta_regime)

# carregando modelo de cadeia de markov
markov_path = os.path.join('MarkovModel.pkl')
markov_model = joblib.load(markov_path)

# criando dados para modelo de markov 
data_markov = yf_data.copy()
data_markov = data_markov.drop('IBC-Br', axis=1)
data_markov['BETA'] = df_with_beta['BETA']
data_markov.dropna(inplace=True)

# criando df de inferencia para cadeia de markov 
df_inference = returns_prices(data_markov)

# funçao para inferencia do modelo de markov
def markov_inference(data:pd.DataFrame):
    scaler = StandardScaler()
    X = scaler.fit_transform(data)
    return markov_model.predict_proba(X)[:,1]

#fazendo inferencia
prob_markov = markov_inference(df_inference)

# conteiner de mudança de regime
regime_row = st.container(border=True)
with regime_row:
    st.metric(label=f"Prob. Atual Regime | date:  {df_inference.index[-1].strftime('%Y/%m/%d')}", value=np.round(prob_markov[-1], 5), delta=f'{risk_bands_func(prob_markov[-1])}', delta_color='orange')

# criando novos states para separaçao de desvios e media
states = pd.qcut(prob_markov, 2, labels=['No regime', 'In Transition'])
df_inference['states'] = states 
df_inference.rename(columns={'vol_petr4':'Volatility_PETR4'}, inplace=True)
std_group_by = df_inference.groupby('states')[['returns','beta', 'Volatility_PETR4']].std()
mean_group_by = df_inference.groupby('states')[['returns','beta', 'Volatility_PETR4']].mean()

group1, group2 = st.columns(2)
with group1:
    st.markdown('Regimes - standard deviation')
    st.dataframe(std_group_by)
with group2:
    st.markdown('Regimes - averages')
    st.dataframe(mean_group_by)


st.markdown("""
    <style>
    .block-container {
        max-width: 90%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)
