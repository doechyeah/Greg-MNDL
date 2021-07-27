from classes import relay
from time import sleep]
from uppertray import UpperTray

# Control all systems and hardware in lower tray
class LowerTray:
    def __init__(self, tray1, tray2, tray3, pumpGPIO):
        self.uppertray1 = UpperTray(tray1[0],tray1[1])
        self.uppertray2 = UpperTray(tray2[0],tray2[1])
        self.uppertray3 = UpperTray(tray3[0],tray3[1])
        self.mainPump = relay.Relay(pumpGPIO, False)
        # self.waterLevel = ______ (Reader for water level)
        self.systemID = None
        self.pumpTimer = 0

    # def directPump(self, )