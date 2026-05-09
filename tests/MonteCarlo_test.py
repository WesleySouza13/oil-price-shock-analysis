import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.analytics.MonteCarloSimulation import MonteCarlo
import os 
import pandas as pd 
data_path = os.path.join('data', 'processed', 'dados_modelagem.csv')
print(os.path.exists(data_path))
data = pd.read_csv(data_path)
data = data[['BETA', 'IBC-Br']]

def test_MonteCarlo():
    mc = MonteCarlo(data).normal_scenario(100)
    mc_sim = MonteCarlo(data).sim_scenario(100, 5, 'IBC-Br')
    
    assert isinstance(mc, pd.DataFrame)
    assert isinstance(mc_sim, pd.DataFrame)

    assert not mc.empty
    assert not mc_sim.empty