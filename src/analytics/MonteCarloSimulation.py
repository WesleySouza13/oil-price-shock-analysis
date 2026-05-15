# %% 
import numpy as np 
import pandas as pd 
from scipy.stats import t
class MonteCarlo():
    def __init__(self, data:pd.DataFrame):
        self.data = data

    def normal_scenario(self,  steps=int) -> pd.DataFrame:
        mc_list = []
        for num in self.data.columns:
            mu = self.data[num].mean()
            std = self.data[num].std()
            mc = np.random.normal(mu, std, steps)
            df = pd.Series(mc, name=num)
            mc_list.append(df)
            
        return pd.concat(mc_list, axis=1)
    
    def sim_scenario(self, n_simulations:int, shock:float, col_shock:str):
        """"use o shock sabendo que sera em %. Ex: 2% -> 2, 3% -> 3..."""
        mc_list = []
        for num in self.data.columns:
            if col_shock in num:
                shock_data = self.data[num] + (self.data[num]* shock/100)
                mu = shock_data.mean()
                std = shock_data.std()
                mc = np.random.normal(mu, std, n_simulations)
                df = pd.Series(mc, name=num)
                mc_list.append(df)
        return pd.concat(mc_list, axis=1)
    
    def T_student_sim(self, n_simulations, col_sim:str):
        col = self.data[col_sim]
        gl = len(col)-1 #graus de liberdade
        t_student = t.rvs(gl, col.mean(), col.std(), n_simulations)
        
        return pd.Series(t_student, name=col_sim)
# %%

