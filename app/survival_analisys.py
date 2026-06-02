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

st.dataframe(new_data)
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

st.markdown("""
        **Cox Model - Features Effects in Survival Curves**
        """)
box1, box2 = st.columns(2)
with box1:
    fig_1 = cph()[1]
    st.pyplot(fig_1)
with box2: 
    fig_2 = cph()[2]
    st.pyplot(fig_2)
    
st.markdown("# Survival Prediction")
start = st.date_input('Start', min_value='2020-01-01', max_value=datetime.date.today(), value='2020-01-01')
end = st.date_input('End', min_value='2020-02-01', max_value=datetime.date.today(), value='2020-02-01')

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
