from src.analytics.Diagnostic import diagnostic
import pandas as pd 
import os 

data = pd.read_csv(os.path.join('data', 'processed', 'dados_modelagem.csv'))
sigma = data['IBC-Br']

def test_diagnostic():
    
    diag = diagnostic(sigma)
    
    assert isinstance(diag, str)
    assert diag is not None