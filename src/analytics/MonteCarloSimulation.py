# %% 
import numpy as np 
import pandas as pd 

class MonteCarlo():
    def __init__(self, data:pd.DataFrame):
        self.data = data

    def normal_scenario(self, n_simulations:int) -> pd.DataFrame:
        np.random.seed(42)
        mc_list = []
        for num in self.data.columns:
            mu = self.data[num].mean()
            std = self.data[num].std()
            
            mc = np.random.normal(mu, std, n_simulations)
            df = pd.Series(mc, name=num)
            mc_list.append(df)
            
        return pd.concat(mc_list, axis=1)
    
    def sim_scenario(self, n_simulations:int, shock:float, col_shock:str):
        """"use o shock sabendo que sera em %. Ex: 2% -> 2, 3% -> 3..."""
        np.random.seed(42)
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
# %%

