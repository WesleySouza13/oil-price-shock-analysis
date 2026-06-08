from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import pandas as pd 
import numpy as np
def hmm_(data:pd.DataFrame):
    print('Fitando modelo de markov')
    returns = np.log(data['Close_PETR4.SA'] / data['Close_PETR4.SA'].shift(1))
    returns = returns.rolling(2).mean()
    vol = returns.rolling(12).std()
    
    data_ = pd.DataFrame({
        'returns':returns,
        'vol_petr4':vol,
        'volume_change': data['Volume_PETR4.SA'].pct_change(),
        'beta':data['BETA'],
        'ibov': data['Close_IBOV'].rolling(12).std()}).dropna()
        
    X = StandardScaler().fit_transform(data_[['returns','vol_petr4','beta']])
    model = hmm.GaussianHMM(n_components=2, random_state=42, n_iter=1000).fit(X)
    states = model.predict(X)
    reg = pd.Series(states, index=data_.index, name='regime')
    prob = model.predict_proba(X)[:,1]
    
    data_['regime'] = states
    data_group = data_.groupby('regime')[['volume_change', 'beta', 'vol_petr4', 'ibov']].mean()
    print(data_group)
    print(f"densidade: {data_['regime'].value_counts(normalize=True)}")
    return reg, prob, model