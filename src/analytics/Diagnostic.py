import pandas as pd 
import numpy as np

def diagnostic(pred:pd.Series): 
    beta_high_mean = np.array(pred)
    text = f"""

    Mean Predict: {round(beta_high_mean.mean(), 3)} 

    Min Value: {round(beta_high_mean.min(),2)}
    
    Max Value: {round(beta_high_mean.max(),2)}

    Std: {round(beta_high_mean.std(),2)} 


    50% of the volatility in this scenario is greater than: {round(np.median(beta_high_mean),3)}
    
    25% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean,75),2)}
    
    10% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean, 90),2)}
    
    5% of the volatility in this scenario is greater than: {round(np.percentile(beta_high_mean, 95),2)}
    """

    return text