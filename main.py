import streamlit as st 
import os 

timeseries_path = os.path.join('app', 'time_series_page.py')
simulation_path = os.path.join('app', 'simulation.py')

time_series = st.Page(timeseries_path, title='Time Series')
simulation = st.Page(simulation_path, title='Simulation')

pg = st.navigation([time_series, simulation])
pg.run()