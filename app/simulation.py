import pandas as pd 
import streamlit as st
from src.data_eng.DataRequest import Requests
from src.analytics.MonteCarloSimulation import MonteCarlo
import datetime
import plotly.express as px
from src.analytics.BetaCalculate import BETA
from src.analytics.PlotSurface import Plot3d
import numpy as np 

st.markdown('# MonteCarlo Simulation')
st.text("""
        In this block, do any simulation using Monte Carlo for simulate diferents scenarios in economy and market.
        
        """)

# simulaçao 
today = datetime.date.today()
start = st.date_input('Start', min_value='2004-01-01', max_value=today)
end =  st.date_input('End', min_value='2005-01-01', max_value=today)

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

surface_beta = Plot3d(data_sim['Close_PETR4.SA'].fillna(data_sim['IBC-Br'].median()), data_sim['Close_IBOV'], data_sim['BETA'], 'BETA Surface with prices')
plot_beta_surface = surface_beta.plot_surface()
st.plotly_chart(plot_beta_surface)


# entradas para a simulaçao 
st.markdown("Select a interval for simulation:")
start_mc = st.date_input('Start', min_value='2004-01-01', max_value=today, key='start_date')
end_mc = st.date_input('End', min_value='2005-01-01', max_value=today, key='end_date')

st.markdown('Simulation Interval - Rolling Window Default: 12')
data_sim = data_sim.loc[start_mc:end_mc]




































st.markdown("""
    <style>
    .block-container {
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)