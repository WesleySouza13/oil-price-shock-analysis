def risk_bands_func(probs:float):
    if probs <0.06 and probs >-0.001:
        return 'No regime'
    if probs > 0.06 and probs <=1:
        return 'In Transition'