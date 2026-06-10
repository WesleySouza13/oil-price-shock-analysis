from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import pandas as pd 
import numpy as np
def returns_prices(data:pd.DataFrame):
    returns = np.log(data['Close_PETR4.SA'] / data['Close_PETR4.SA'].shift(1))
    returns = returns.rolling(2).mean()
    vol = returns.rolling(12).std()
    
    return pd.DataFrame({
        'returns':returns,
        'vol_petr4':vol,
        'beta':data['BETA']}).dropna()
        
