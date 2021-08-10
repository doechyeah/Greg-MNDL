import threading, os, time, json, signal
import requests as req
from classes import uppertray, lowertray
from redis import Redis
from rq import Queue


"""
Start Webservice and Celery worker 
"""
redis_conn = Redis()
fill_queue = Queue('fill', connection=redis_conn)

# app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)
# start celery work with and redis
# $ redis-server
# $ celery -A <Application Name>.celery worker -l info

"""
System Infromation and managment objects
"""
# Load System Information.
with open('/home/pi/Greg-MNDL/operationbox/system_info.json') as f:
    sys_info = json.loads(f.read())

systemID = sys_info["LowerTray"]["systemID"]
trays = [ uppertray.UpperTray(gpio[0], gpio[1]) for _, gpio in sys_info["UpperTrayGPIO"].items() ]
lower_tray = lowertray.LowerTray(systemID, sys_info["LowerTray"]["pumpGPIO"])
systemLED = sys_info["LowerTray"]["systemLED"]


# Registry keeps track of which deviceID is assigned to which tray
# ex. { "<deviceID>" : [ UpperTrayObject, "<Available for job>"]}
# registry = dict()

# Queue manages the filling of trays
#fill_queue = queue.Queue()

# Threaded Queue that services all trays
def service_Tray(devID, position):
    if True:
        # Threaded operation to check if any tray needs to be filled
        #print(devQ.qsize())
        #devID = devQ.get()
        request = {"position" : position,
                    "deviceID" : devID}
        try:
            lower_tray.mainPump_on()
            # position = registry.get(devID)[0]
            utray = trays[position]
            print(f"Filling Upper Tray: {position}")
            result = utray.fill_tray(time=30)
            if result == -1:
                # Error occurred while opening valve
                print("Error with fill_tray")
                raise Exception
            # Allow pump to run for 50 seconds to be fill tray
            lower_tray.mainPump_off()
            print(f"Letting Upper Tray {position} soak and drain (Launching celery task)")
            # Launch celery task to handle when to drain the tray
            # task = drainStart.delay(position, devID)
            # request["taskID"] = str(task)
        except Exception as e:
            print("Error caught during task")
            print(e.message, e.args)
        finally:
            # Cleanup
            # Ensure pump is turned off
            lower_tray.mainPump_off()
            print(json.dumps(request))
            tresp = req.put("http://localhost/startdrain", json=request )
            #print(devQ.qsize())
            #devQ.task_done()