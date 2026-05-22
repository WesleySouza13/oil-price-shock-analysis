import streamlit as st 
from src.data_eng.DataRequest import Requests
import datetime as dt 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np 
import pandas as pd 
from src.analytics.PlotSurface import Plot3d
import os 

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
print(data)


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
            # Bem vindo (a)
            
            
            """)

fig_line = px.line(x=data.index, y=data['IBC-Br'])
fig_line.update_layout(xaxis_title='Tempo', title='Histórico - IBC-Br', width=850, yaxis_title='IBC-Br')

fig_petr4 = go.Figure()
fig_petr4.add_trace(go.Scatter(x=petr4.index, y=petr4, mode='lines', name='PETR4', line=dict(color="#0011FF", width=3)))
fig_petr4.update_layout(title='Histórico - PETR4.SA', xaxis_title='Tempo', width=350)

fig_ibov = go.Figure()
fig_ibov.add_trace(go.Scatter(x=ibov_.index, y=ibov_, mode='lines', name='^IBOV', line=dict(color="#ff0000", width=3)))
fig_ibov.update_layout(title='Histórico - IBOVESPA', xaxis_title='Tempo', width=350)


# plotando grafico do IBC-Br 

st.plotly_chart(fig_line)

col1, col2 = st.columns(2, gap='large')
with col1:
    st.plotly_chart(fig_ibov, use_container_width=True)
    
with col2:
    st.plotly_chart(fig_petr4, use_container_width=True)
    

# calculando coeficiente beta 
#st.text("Historico de sensibilidade dos preços ao longo do tempo por Coeficiente Beta")
#window = st.number_input('Digite o janelamento (em Meses):', min_value=12, max_value=100)
# funçao para o calculo de BETA 
def BETA(petra:pd.Series, ibov:pd.Series): 
    data = pd.concat([petra, ibov], join='inner', axis=1).dropna()
    returns = data.pct_change()
    cov = returns['Close_PETR4.SA'].rolling(12).cov(returns['Close_IBOV'])
    var = returns['Close_IBOV'].rolling(12).var()
    data['BETA'] = cov/var
    return data.dropna()


st.markdown('# Formulação - Índice Beta')
st.text("""O índice Beta foi usado nesse trabalho para trabalhar como um indicador de sensibilidade do ativo pelo mercado. 
            A fórmula é a razão entre a covariância do retorno do ativo e do mercado, com a variância do mercado. 
            
            Em nosso caso, como estamos explorando o sinal de volatilidade do petróleo Brasileiro, vamos usar o PETR4.SA (PetroBras) em conjunto com o ^IBOV (IBOVESPA).
        
        """)
beta_img_path = os.path.join('img', 'formula_beta.png')
st.image(beta_img_path)

df_with_beta = BETA(petr4, ibov_)
fig_beta = go.Figure()
fig_beta.add_trace(go.Scatter(x=df_with_beta.index, y=df_with_beta['BETA'], mode='lines', name='Beta', line=dict(color="#26ff00", width=3)))
fig_beta.update_layout(title='Histórico - BETA', xaxis_title='Tempo', yaxis_title='Beta')
st.plotly_chart(fig_beta, use_container_width=True)

# mostrando dataframe
df_with_beta['IBC-Br'] = data['IBC-Br']
st.dataframe(df_with_beta)

# calculando sigma (volatilidade)
def calculate_sigma(petr4:pd.Series):
    ret = np.log(petr4)/petr4.shift()
    return ret.rolling(3).std().shift(-3)

df_with_beta['sigma'] = calculate_sigma(df_with_beta['Close_PETR4.SA'])
# plotando linhas do sigma 
fig_sigma = go.Figure()
fig_sigma.add_trace(go.Scatter(x=df_with_beta.index, y=df_with_beta['sigma'], mode='lines', name='Beta', line=dict(color="#26ff00", width=3)))
fig_sigma.update_layout(title='Volatilidade PETR4.SA', xaxis_title='Tempo', yaxis_title='Sigma')
st.plotly_chart(fig_sigma)

# plotando area do sigma 
surface  = Plot3d(df_with_beta['IBC-Br'], df_with_beta['BETA'], df_with_beta['sigma'], 'Área - Volatilidade por IBC-Br e Beta')
surface1 = surface.plot_surface()
st.plotly_chart(surface1, use_container_width=True)