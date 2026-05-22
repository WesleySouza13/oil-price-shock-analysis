import numpy as np 
import pandas as pd 
from scipy.interpolate import griddata
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Plot3d():
    def __init__(self, x:pd.Series, y:pd.Series, z:pd.Series, title:str):
        self.x = x
        self.y = y
        self.z = z 
        self.title = title 
    def plot_surface(self):
        x_data = np.array(self.x)
        y_data = np.array(self.y)
        z_data = np.array(self.z)
        
        #criando grid para plot 
        X, Y = np.meshgrid(np.linspace(x_data.min(), x_data.max(), 50),
                            np.linspace(y_data.min(), y_data.max(), 50))
        Z = griddata((x_data, y_data), z_data, (X, Y), method='linear')
        
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'surface'}, {'type': 'scene'}]])    
        fig.add_trace(go.Surface(x=X, y=Y, z=Z), row=1,col=1)
        fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True))
        fig.update_layout(title=self.title,autosize=False,width=1400,height=700, margin=dict(l=65, r=50, b=65, t=90))
        
        fig.add_trace(go.Scatter3d(x=x_data,y=y_data,z=z_data,mode='markers',marker=dict(size=4)),row=1,col=2)    
        fig.update_scenes(xaxis_title=self.x.name,yaxis_title=self.y.name,zaxis_title=self.z.name,row=1,col=1)
        fig.update_scenes(xaxis_title=self.x.name,yaxis_title=self.y.name,zaxis_title=self.z.name,row=1,col=2)

        return fig