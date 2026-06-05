import streamlit as st 
import os 

timeseries_path = os.path.join('app', 'time_series_page.py')
simulation_path = os.path.join('app', 'simulation.py')
survival_path = os.path.join('app', 'survival_analisys.py')
about_path = os.path.join('app', 'about_me.py')

time_series = st.Page(timeseries_path, title='Time Series', icon='📈')
simulation = st.Page(simulation_path, title='Simulation', icon='⚙️')
survival = st.Page(survival_path, title='Survival Analisys', icon='💀')
about = st.Page(about_path, title='About Me', icon='👋🏽')
pg = st.navigation([about, time_series, simulation, survival])
pg.run()