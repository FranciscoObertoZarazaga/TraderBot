import Config


def setTurnOff(turnOffVal):
    Config.TURN_OFF_LOCK.acquire()
    Config.TURN_OFF = turnOffVal
    Config.TURN_OFF_LOCK.release()
