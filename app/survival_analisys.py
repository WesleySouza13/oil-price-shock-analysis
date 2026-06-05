import streamlit as st 
from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter
import os 
import pandas as pd 
import plotly.express as px
from lifelines.calibration import survival_probability_calibration
import matplotlib.pyplot as plt
import numpy as np 
import datetime 
from src.data_eng.DataRequest import Requests

st.markdown("# Welcome to Survival Analisys")

data_path = os.path.join('data', 'processed', 'survival_data.csv')
data_path_features = os.path.join('data', 'processed', 'dados_modelagem.csv')
data = pd.read_csv(data_path)
#data = data.drop('data', axis=1)
data['data'] = pd.to_datetime(data['data'], errors='coerce')
df = pd.read_csv(data_path_features)
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df = df[['data','Produção de derivados de petróleo', 'IBC-Br', 'Close_PETR4.SA', 'Close_IBOV']]
new_data = pd.merge(data, df, how='inner', on='data')

#dropando coluna de datas nesse df pois vou usar ele em kaplanmeier
data = data.drop('data', axis=1)

# o mesmo efeito sera realizado em new df 
new_data = new_data.drop('data', axis=1)
def survival_model():
    model = KaplanMeierFitter().fit(data['t'], data['regime'])
    return model.survival_function_

survival_f = survival_model()
fig = px.line(survival_f)
fig.update_layout(title='Survival Curve - Kaplan Meier', xaxis_title='Steps', yaxis_title='Prob.')
st.plotly_chart(fig)

#criando modelo de hazard 
def cph():
    cph_model = CoxPHFitter()
    cph_model.fit(new_data, duration_col='t', event_col='regime')
    fig, axes = plt.subplots(figsize=(15,12))
    
    cph_model.plot_partial_effects_on_outcome(covariates='Produção de derivados de petróleo', values=[np.percentile(new_data['Produção de derivados de petróleo'], 20), np.percentile(new_data['Produção de derivados de petróleo'], 50), np.percentile(new_data['Produção de derivados de petróleo'], 90)], ax=axes)
    fig2, axes2 =  plt.subplots(figsize=(15,14))
    cph_model.plot(ax=axes2)
    
    return cph_model.print_summary(), fig, fig2


st.markdown("# Survival Prediction")
start = st.date_input('Start', min_value='2019-01-01', max_value=datetime.date.today(), value='2020-01-01')
end = st.date_input('End', min_value='2019-02-01', max_value=datetime.date.today(), value='2020-05-01')

#pegando dados 
codes = ['1389', '24364']
req = Requests(codes)
get_data = req.get_data(start=start.strftime('%d/%m/%Y'), end=end.strftime('%d/%m/%Y'))
df_req = req.get_dataframe()
petr4 = req.y_finance_req(['PETR4.SA'], start, end)
ibov = req.get_ibov('^BVSP', start, end)

# dataframe para previsoes
petr4['Close_IBOV'] = ibov['Close_IBOV']
df_pred = petr4.copy()

# fazendo previsoes com modelo de Kaplan 
cox_model = CoxPHFitter().fit(new_data, duration_col='t', event_col='regime') # re-treinando o modelo 
pred_cox = cox_model.predict_survival_function(df_pred)
prob = 1 - pred_cox.iloc[-1]
prob_fig = px.line(prob,color_discrete_sequence=['red'] )
prob_fig.update_layout(title='Predicted Event Risk by Scenario', xaxis_title='date', yaxis_title='predict')
st.plotly_chart(prob_fig)
prob_sequence = 1-pred_cox


prob_heatmap = px.imshow(prob_sequence, color_continuous_scale='RdBu_r')
prob_heatmap.update_layout(title='Probability of the Event - Heatmap', yaxis_title='steps')
st.plotly_chart(prob_heatmap)

prob.index = prob.index.strftime('%Y-%m-%d')
max_probIndex = prob.idxmax()
max_prob = prob.max()
min_probIndex = prob.idxmin()
min_prob = prob.min()
col1, col2 = st.columns(2)

#criando previsoes para datas em risco
df_pred.index = df_pred.index.strftime('%Y-%m-%d')
survival_curve = cox_model.predict_survival_function(df_pred)
survival_curve = survival_curve[[max_probIndex, min_probIndex]]

#plotando figura filtradas 
survival_fig = px.line(survival_curve, color_discrete_sequence=['red', 'orange'])
survival_fig.update_layout(title='Event Risk Dates - Survival Curves', xaxis_title='steps', yaxis_title='Survival Prob.')
st.plotly_chart(survival_fig)
with col1:
        with st.container(border=True):
            st.write('Hightest Event Risk:')
            st.text(f'Date: {max_probIndex}')
            st.write(max_prob*100,'%')
        
with col2:
        with st.container(border=True):
            st.write('Lowest Event Risk:')
            st.text(f'Date: {min_probIndex}')
            st.write(round(min_prob*100,3),'%')
        
coef = cox_model.params_
with st.container(border=True):
    for value, name in zip(coef,df_pred.columns ):
        st.write(f'Feature: {name} | Coef ',round(value,4))
