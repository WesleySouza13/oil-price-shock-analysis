import streamlit as st 
import os 

timeseries_path = os.path.join('app', 'time_series_page.py')
simulation_path = os.path.join('app', 'simulation.py')
prev_path = os.path.join('app', 'forecast.py')

time_series = st.Page(timeseries_path, title='Time Series', icon='📈')
simulation = st.Page(simulation_path, title='Simulation', icon='⚙️')
forecast = st.Page(prev_path, title='Forecast', icon='🔮')
pg = st.navigation([time_series, simulation, forecast])
pg.run()