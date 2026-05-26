from src.analytics.BetaCalculate import BETA
import numpy as np
import pandas as pd 
import os 

data_path = os.path.join('data', 'processed', 'dados_modelagem.csv')
data = pd.read_csv(data_path)
def test_beta():
    
    beta = BETA(data['Close_PETR4.SA'], data['Close_IBOV'])
    
    assert beta is not None 
    assert beta.shape[1] == 3 
    assert not beta.empty