import pandas as pd 
import streamlit as st
from src.data_eng.DataRequest import Requests
from src.analytics.MonteCarloSimulation import MonteCarlo
import datetime
import plotly.express as px
from src.analytics.BetaCalculate import BETA
from src.analytics.PlotSurface import Plot3d
import numpy as np 
import joblib 
import os 
import plotly.graph_objects as go
from datetime import date
from scipy.stats import t
st.markdown('# MonteCarlo Simulation')
st.text("""
        In this block, do any simulation using Monte Carlo for simulate diferents scenarios in economy and market.
        
        """)

# simulaçao 
today = datetime.date.today()
start = st.date_input('Start', value=date(2020,1,1), min_value=date(2004, 1,1), max_value=today, key='Start')
end =  st.date_input('End', value=today, min_value=start, max_value=today, key='End')

req = Requests(['24364', '433'])
start_req = start.strftime('%d/%m/%Y')
end_req = end.strftime('%d/%m/%Y')

data_req = req.get_data(start_req, end_req)
data = req.get_dataframe()
data = data.drop('IPCA', axis=1) # usei o ipca so como pivor minimo da requisiçao
price = req.y_finance_req(['PETR4.SA'], start, end)

# pegando preços e calculando beta
ibov = req.get_ibov(['^BVSP'], start, end)
data['Close_PETR4.SA'] = price['Close_PETR4.SA']
data['Close_IBOV'] = ibov['Close_IBOV']
beta = BETA(data['Close_PETR4.SA'], data['Close_IBOV'])
data['BETA'] = beta['BETA']
data_sim  = data.loc[start:end]

#mostrando dataframe
st.dataframe(data_sim)

if data_sim.empty:
    st.text('Input a valid interval.')

col1, col2, col_box = st.columns(3)
fig = px.line(x=data_sim.index, y=data_sim['IBC-Br'])
fig.update_layout(title='Historical - IBC-Br', xaxis_title='Time', yaxis_title='IBC-Br')

fig2 = px.histogram(data_sim['IBC-Br'])
fig2.update_layout(title='Distribution - IBC-Br', xaxis_title='IBC-Br', yaxis_title='Frequency')

box1 = px.box(data_sim['IBC-Br'])
box1.update_layout(title='Boxplot', yaxis_title='Value')

with col1:
    st.plotly_chart(fig, width='stretch')

with col2: 
    st.plotly_chart(fig2,  width='stretch')
    
with col_box: 
    st.plotly_chart(box1,  width='stretch')

col3, col4, col_box2 = st.columns(3)

fig3 = px.line(x=data_sim.index, y=data_sim['BETA'])
fig3.update_layout(title='Historical - BETA',  xaxis_title='Time', yaxis_title='BETA')

fig4 = px.histogram(data_sim['BETA'], nbins=20)
fig4.update_layout(title='Distribuition - BETA',  xaxis_title='BETA', yaxis_title='Frequency')

box2 = px.box(data_sim['BETA'])
box2.update_layout(title='Boxplot', yaxis_title='Value')

with col3: 
    st.plotly_chart(fig3,  width='stretch')
with col4:
    st.plotly_chart(fig4,  width='stretch')
with col_box2:
    st.plotly_chart(box2,  width='stretch')

surface_beta = Plot3d(data_sim['Close_IBOV'], data_sim['Close_PETR4.SA'], data_sim['BETA'], 'BETA Surface with prices')
plot_beta_surface = surface_beta.plot_surface()
st.plotly_chart(plot_beta_surface)


# entradas para a simulaçao 
st.markdown("Select a interval for simulation:")
start_mc = st.date_input('Start', value=date(2020,1,1),min_value='2004-01-01', max_value=today, key='start_date')
end_mc = st.date_input('End', min_value='2005-01-01', max_value=today, key='end_date')
scenarios = st.number_input('Scenarios', min_value=2, max_value=36, value=12)
st.markdown('Simulation Interval - Rolling Window Default: 12')
data_sim = data_sim.loc[start_mc:end_mc]

# montecarlo 
mc = MonteCarlo(data_sim[['IBC-Br','BETA']])
mc_normal = mc.normal_scenario(scenarios)

fig_mc1, fig_mc2 = st.columns(2)
fig_mc = px.histogram(mc_normal['IBC-Br'])
fig_mc.update_layout(title='IBC-Br - Normal Simulation', yaxis_title='Frequency')
fig_mc_beta = px.histogram(mc_normal['BETA'])
fig_mc_beta.update_layout(title='BETA - Normal Simulation', yaxis_title='Frequency')

with fig_mc1:
    st.plotly_chart(fig_mc)

with fig_mc2:
    st.plotly_chart(fig_mc_beta)

st.dataframe(mc_normal)
# carregando dados de treino para o modelo ver e fazer inferencia 
data_train = os.path.join('data', 'processed', 'dados_modelagem.csv')
data = pd.read_csv(data_train)
y_train = data[['data','IBC-Br', 'BETA']]
y_train = y_train.set_index('data')
y_train = y_train.loc['2004-01-01':'2024-06-01']

# carregando modelo
model_path = os.path.join('modelARDL.pkl')
model = joblib.load(model_path)
model.model.data.dates = None
model.model.data.freq = None
model.model._index = pd.RangeIndex(len(y_train))
model.model._index_generated = False
model._index = pd.RangeIndex(start=0, stop=len(data))

def predict(exog):
    return model.predict(start=len(y_train),end=len(y_train) + len(exog) - model.model._maxlag - 1,exog_oos=exog)

normal_pred = predict(mc_normal)
hist_normal = px.histogram(normal_pred)
hist_normal.update_layout(title='Distribuition Sigma - Normal scenarios [No Shocks]',  yaxis_title='Frequency')
st.plotly_chart(hist_normal)
normal_surf = Plot3d(mc_normal['IBC-Br'][:len(normal_pred)], mc_normal['BETA'][:len(normal_pred)], normal_pred, title='Area Sigma - Normal Simulation')
st.plotly_chart(normal_surf.plot_surface())

# criando shocks 
box = st.container(border=True)
st.warning('Input the shocks without percents, for example, if want do a simulation, use: 2% -> 2, 50% -> 50...', icon='🚨')

with box: 
    shock_ibc = st.number_input('Input Shock in IBC-Br')
    shock_beta = st.number_input('Input Shock in BETA')

simulations = st.number_input('Simulations', min_value=2, max_value=5000)
st.markdown('Default: 2 simulations')

# fazendo multiplas simulaçoes
pred_list = []
df_sim_list = []
fig_plot_sim = go.Figure()
fig_plot_ibc = go.Figure()
fig_plot_beta = go.Figure()
for _ in range(simulations):
    ibc = mc.T_student_shocks(scenarios, shock_ibc, 'IBC-Br')
    beta = mc.T_student_shocks(scenarios, shock_beta, 'BETA')
    df_sim = pd.concat([ibc, beta], axis=1)
    predict_sim = predict(df_sim)
    pred_series = pd.Series(predict_sim, name='Sigma')
    y_hat = np.cumsum(predict_sim)/np.arange(len(predict_sim))
    pred_list.append(pred_series)
    df_sim_list.append(df_sim)
    fig_plot_sim.add_trace(go.Scatter(y=y_hat,mode='lines',line=dict(width=1),showlegend=False))
    
    #plotando horizontes de simualçao
    #criando graficos
    fig_plot_ibc.add_trace(go.Scatter(y=ibc.values, mode='lines'))
    fig_plot_beta.add_trace(go.Scatter(y=beta.values, mode='lines'))

fig_plot_sim.update_layout(title=f'Sigma Simulations: {simulations}', xaxis_title='steps', yaxis_title='mean', showlegend=False)
fig_plot_ibc.update_layout(title=f'IBC-Br - Simulations: {simulations}', xaxis_title='steps', yaxis_title='values', showlegend=False)
fig_plot_beta.update_layout(title=f'BETA - Simulations: {simulations}', xaxis_title='steps', yaxis_title='values', showlegend=False)
#plotando com o streamlit
col1_plot, col2_plot = st.columns(2)

with col1_plot:
    st.plotly_chart(fig_plot_ibc, use_container_width=True, key='ibc-br')
with col2_plot:
    st.plotly_chart(fig_plot_beta, use_container_width=True, key='beta_')

st.plotly_chart(fig_plot_sim)

#juntando previsoes e variaveis independentes
pred_concat = pd.concat(pred_list)
df_sim_concat = pd.concat(df_sim_list)
plot_sim_area = Plot3d(df_sim_concat['IBC-Br'][:len(pred_concat)], df_sim_concat['BETA'][:len(pred_concat)], pred_concat, title=f'Area Sigma - IBC-Br Shock: {shock_ibc}% | BETA Shock: {shock_beta}%')
st.plotly_chart(plot_sim_area.plot_surface())
def diagnostic(pred): 
    beta_high_mean = np.array(pred)
    text = f"""

    Mean Predict: {round(beta_high_mean.mean(), 3)} 

    Min Value: {round(beta_high_mean.min(),2)}
    
    Max Value: {round(beta_high_mean.max(),2)}

    Std: {round(beta_high_mean.std(),2)} 


    50% of the volatility in this scenario is greater than: {round(np.median(beta_high_mean),3)}
    
    25% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean,75),2)}
    
    10% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean, 90),2)}
    
    5% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean, 95),2)}
    """

    return text
# caixa para diagnosticos
box2 = st.container(border=True)
with box2:
    st.write(diagnostic(pred_list))

# calculando integvalos de confiança
def confiance_interval(pred:pd.Series, conf:float):
    conf_ = conf/100
    sample = pred.sample(len(pred), replace=True)
    alpha = 1-conf_
    t_ = t.ppf(1-alpha/2, len(pred)-1)
    inf_limit = sample.mean() - t_ * (sample.std()/len(sample)**0.5)
    sup_limit = sample.mean() + t_ * (sample.std()/len(sample)**0.5)

    return inf_limit, sup_limit
confiance = st.number_input('Confidence:', min_value=50, max_value=99)
#confiance_interval_ = confiance_interval(pred_concat, confiance)
# verificando diferentes simulaçoes por intervalo de confiança 
if confiance: 
    real_mean = pred_concat.mean()
    ci_simulations = st.number_input('CI Simulations', min_value=2, max_value=10000, key='ci_sim')
    
    ci_list = []
    for _ in range(ci_simulations):
        ic = confiance_interval(pred_concat, confiance)
        ci_list.append(ic)
        
df_ci = pd.DataFrame(ci_list, columns=['inf', 'sup'])
df_ci['True_Mean'] = real_mean
df_ci['Confiance'] = (df_ci['True_Mean']>df_ci['inf']) & (df_ci['True_Mean']<df_ci['sup'])
df_ci['Confiance'] = df_ci['Confiance'].replace(True, 1)
df_ci['Confiance'] = df_ci['Confiance'].replace(False, 0)

st.dataframe(df_ci)

conf_row = st.container(border=True)

with conf_row:
    st.metric(value=np.round(df_ci['Confiance'].mean(),2), label='Simulations Confiance (%)', delta=round(df_ci['Confiance'].mean() - (confiance/100),2))

st.markdown("""
    <style>
    .block-container {
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)