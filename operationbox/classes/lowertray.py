import relay
from time import sleep

# Control all systems and hardware in lower tray
class LowerTray:
    def __init__(self, systemID, pumpGPIO):
        self.mainPump = relay.Relay(pumpGPIO, False)
        # self.waterLevel = ______ (Reader for water level)
        self.systemID = systemID
        self.water_level = 50
        self.pumpTimer = 0

    def mainPump_on(self):
        self.mainPump.on()
    
    def mainPump_off(self):
        self.mainPump.off()
    
    def check_Water(self):
        ### Check water level of tank
        print(1)
