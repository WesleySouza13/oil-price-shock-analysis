from src.analytics.RiskBandsFunc import risk_bands_func

def test_bands():
    bands = risk_bands_func(0)
    bands1 = risk_bands_func(1)
    
    assert bands is not None
    assert isinstance(bands, str)
    
    assert bands1 is not None
    assert isinstance(bands1, str)