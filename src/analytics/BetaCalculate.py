import pandas as pd 

def BETA(petra:pd.Series, ibov:pd.Series): 
    data = pd.concat([petra, ibov], join='inner', axis=1).dropna()
    returns = data.pct_change()
    cov = returns['Close_PETR4.SA'].rolling(12).cov(returns['Close_IBOV'])
    var = returns['Close_IBOV'].rolling(12).var()
    data['BETA'] = cov/var
    return data.dropna()