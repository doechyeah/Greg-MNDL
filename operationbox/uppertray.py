from classes import relay
from time import sleep

class UpperTray:
    def __init__(self, inGPIO, outGPIO):
        self.inflow = relay.Relay(inGPIO, False)
        self.outflow = relay.Relay(outGPIO,False)
        # self.deviceID = None

    def fill_tray(self, time = 50):
        try:
            # if self.deviceID is None:
            #     print("System is not registered:\nSKIPPING OPERATION -- PLEASE REGISTER TRAY BEFORE USING")
            #     return -1
            self.inflow.on()
            sleep(time)
            self.inflow.off()
        except Exception as Err:
            print(f"An Error has occurred in the system: {Err}")
            return -1
        return 1

    def drain_tray(self, time = 200):
        # if self.deviceID is None:
        #     print("System is not registered:\nSKIPPING OPERATION -- PLEASE REGISTER TRAY BEFORE USING")
        #     return -1
        self.outflow.on()
        sleep(time)
        self.outflow.off()

    # def register_tray(self, deviceID):
    #     self.deviceID = deviceID
    
    # def unregister_tray(self):
    #     self.deviceID = None

    # def get_deviceID(self):
    #     return self.deviceID

