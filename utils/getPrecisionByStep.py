from math import log, floor


def getPrecisionByStep(step):
    step = float(step)
    return floor(log(round(1/step), 10))
