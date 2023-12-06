from Config import EXCHANGES


def setArbitrator(arbitrator):
    for exchange in EXCHANGES:
        exchange.setArbitrator(arbitrator)
