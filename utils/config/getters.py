import Config


def getTurnOff():
    Config.TURN_OFF_LOCK.acquire()
    turnOffAux = Config.TURN_OFF
    Config.TURN_OFF_LOCK.release()
    return turnOffAux
