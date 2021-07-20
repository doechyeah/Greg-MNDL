from time import sleep
import RPi.GPIO as GPIO
import cv2
import os, json, datetime

class Plant_System:
    # Creates object of plant system to service.
    def __init__(self):
        with open("operationbox/system_info.json") as f:
            sys_info = json.load(f)
        sys_info["system_stats"]["startTime"] = datetime.now()

        self.mapping = sys_info["mapping"]
        self.system_stats = sys_info["system_stats"]
        self.op_info = sys_info["op_info"]

        with open("operationbox/system_info.json") as f:
            json.dump(sys_info, f)
    
    def updateStats(self):
        self.system_stats["totalTime"] = self.system_stats["totalTime"] + 
        res = {**self.op_info, **self.system_stats, **self.system_stats}
        with open("operationbox/system_info.json") as f:
            json.dump(res, f)
        
