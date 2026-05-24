import streamlit as st 
from src.analytics.MonteCarloSimulation import MonteCarlo
import os 
import pandas as pd 
import datetime
import plotly.express as px 


st.markdown('# MonteCarlo Simulation')
st.text("""
        In this block, do any simulation using Monte Carlo for simulate diferents scenarios in economy and market.
        
        """)
data_path = os.path.join('data', 'processed', 'dados_modelagem.csv')
data = pd.read_csv(data_path)
data['data'] = pd.to_datetime(data['data'], errors='coerce')
data = data.set_index('data')
data = data[['IBC-Br', 'BETA']]

st.markdown('Historical DataFrame')
st.dataframe(data)

# simulaçao 
today = datetime.date.today()
start = st.date_input('Start', min_value='2004-01-01', max_value=today)
end =  st.date_input('End', min_value='2005-01-01', max_value=today)

data_sim  = data.loc[start:end]
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
    st.plotly_chart(fig, use_container_width=True, width='stretch')

with col2: 
    st.plotly_chart(fig2, use_container_width=True, width='stretch')
    
with col_box: 
    st.plotly_chart(box1, use_container_width=True, width='stretch')

col3, col4, col_box2 = st.columns(3)

fig3 = px.line(x=data_sim.index, y=data_sim['BETA'])
fig3.update_layout(title='Historical - BETA',  xaxis_title='Time', yaxis_title='BETA')

fig4 = px.histogram(data_sim['BETA'], nbins=20)
fig4.update_layout(title='Distribuition - BETA',  xaxis_title='BETA', yaxis_title='Frequency')

box2 = px.box(data_sim['BETA'])
box2.update_layout(title='Boxplot', yaxis_title='Value')

with col3: 
    st.plotly_chart(fig3, use_container_width=True, width='stretch')
with col4:
    st.plotly_chart(fig4, use_container_width=True, width='stretch')
with col_box2:
    st.plotly_chart(box2, use_container_width=True, width='stretch')