
def risk_bands_func(probs:float) -> str:
    if probs <0.000274 and probs >-0.001:
        return 'No regime'
    if probs > 0.000274 and probs <=1:
        return 'In Transition'