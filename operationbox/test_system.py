from classes import lowertray, uppertray
from time import sleep, time
import threading, json
import RPi.GPIO as GPIO

with open('system_info.json') as f:
    sys_info = json.loads(f.read())

class Test_System:
    def __init__(self, upperGPIO=sys_info["UpperTrayGPIO"], Lower=sys_info["LowerTray"], fill_t=50, drain_t=200):
        self.trays = [ uppertray.UpperTray(gpio[0], gpio[1]) for _, gpio in upperGPIO.items() ]
        self.lower_tray = lowertray.LowerTray(Lower["systemID"], int(Lower['pumpGPIO']))
        self.fill_t = fill_t
        self.drain_t = drain_t
        GPIO.setmode(GPIO.BCM)
        self.wifiLED = Lower["wifiLED"]
        self.systemLED = Lower["systemLED"]
        GPIO.setup(self.wifiLED, GPIO.OUT)
        GPIO.setup(self.systemLED, GPIO.OUT)
        GPIO.output(self.wifiLED, GPIO.HIGH)

    def test_single(self, position):
        try:
            GPIO.output(self.systemLED, GPIO.HIGH)
            self.lower_tray.mainPump_on()
            self.trays[position].fill_tray(time=self.fill_t)
            self.lower_tray.mainPump_off()
            sleep(5)
            self.trays[position].drain_tray(time=self.drain_t)
        except:
            print("ERROR OCCURRED DURING TASK")
        finally:
            self.lower_tray.mainPump_off()
            GPIO.output(self.systemLED, GPIO.LOW)
    
    def test_all(self):
        try:
            GPIO.output(self.systemLED, GPIO.HIGH)
            self.lower_tray.mainPump_on()
            fill_threads = list()
            for tray in self.trays:
                x = threading.Thread(target=tray.fill_tray, args=(self.fill_t,), daemon=True)
                fill_threads.append(x)
                x.start()
            for thread in fill_threads:
                thread.join()
            self.lower_tray.mainPump_off()
            sleep(5)
            drain_threads = list()
            for tray in self.trays:
                x = threading.Thread(target=tray.drain_tray, args=(self.drain_t,), daemon=True)
                drain_threads.append(x)
                x.start()
            for thread in drain_threads:
                thread.join()
        except:
            print("ERROR OCCURRED DURING TASK")
        finally:
            self.lower_tray.mainPump_off()
            GPIO.output(self.systemLED, GPIO.LOW)
