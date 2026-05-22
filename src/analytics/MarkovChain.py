from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import numpy as np 
import pandas as pd 

def MarkovModel(data:pd.DataFrame):
    print('Fitando modelo de markov')
    returns = np.log(data['Close_PETR4.SA'] / data['Close_PETR4.SA'].shift(1))
    returns = returns.rolling(2).mean()
    vol = returns.rolling(12).std()
    
    data_ = pd.DataFrame({
        'returns':returns,
        'vol':vol,
        #'volume_change': data['Volume_PETR4.SA'].pct_change(),
        'beta':data['BETA'],
        'ibov': data['Close_IBOV'].rolling(12).std(), 
        'sigma': data['Sigma']}
        ).dropna()
        
        
    X = StandardScaler().fit_transform(data_[['returns','beta', 'ibov', 'vol', 'sigma']])
    model = hmm.GaussianHMM(n_components=2, random_state=42, n_iter=1000).fit(X)
    states = model.predict(X)
    #data_['regime'] = states
    #data_group = data_.groupby('regime')[['volume_change', 'beta', 'vol_petr4', 'ibov']].mean()
    #print(data_group)
    #print(f"densidade: {data_['regime'].value_counts(normalize=True)}")
    return pd.Series(states, index=data_.index, name='regime').fillna(0)