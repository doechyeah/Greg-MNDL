# from logging import raiseExceptions
from flask import Flask, jsonify, request
import threading, os, time, json, signal #, queue
from celery import Celery
import requests as req
from classes import uppertray, lowertray
import RPi.GPIO as GPIO
import sherlock
from sherlock import Lock

"""
Start Webservice and Celery worker 
"""
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# start celery work with and redis
# $ redis-server
# $ celery -A <Application Name>.celery worker -l info

sherlock.configure(backend=sherlock.backends.REDIS,
                   expire=None,
                   retry_interval=0.1)

pumpLock = Lock('mainPump')

# Cleanup Signal
def quit_Greg(*args):
    print('Stopping Greg System')
    # Turn off LED here
    exit(0)

"""
System Infromation and managment objects
"""
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Load System Information.
with open('/home/pi/Greg-MNDL/operationbox/system_info.json') as f:
    sys_info = json.loads(f.read())

systemID = sys_info["LowerTray"]["systemID"]
trays = [ uppertray.UpperTray(gpio[0], gpio[1]) for _, gpio in sys_info["UpperTrayGPIO"].items() ]
lower_tray = lowertray.LowerTray(systemID, sys_info["LowerTray"]["pumpGPIO"])
systemLED = sys_info["LowerTray"]["systemLED"]
GPIO.setup(systemLED, GPIO.OUT)

# Registry keeps track of which deviceID is assigned to which tray
# ex. { "<deviceID>" : [ UpperTrayObject, "<Available for job>"]}
registry = dict()

# Queue manages the filling of trays
#fill_queue = queue.Queue()


"""
Service Functions
"""
@celery.task(bind=True)
def servceTray(self, deviceID, position, soak_t=6):
    # request = {"systemID" : systemID,
    #             "deviceID" : deviceID,
    #             "taskID" : None,
    #             "status" : True}
    try:
        pumpLock.acquire()
        lower_tray.mainPump_on()
        utray = trays[position]
        print(f"Filling Upper Tray: {position}")

        utray.fill_tray(time=10)
        # Allow pump to run for 50 seconds to be fill tray
        lower_tray.mainPump_off()
        pumpLock.release()
        print(f"Letting Upper Tray {position} soak and drain (Launching celery task)")
        # Launch celery task to handle when to drain the tray
        # task = drainStart.delay(position, deviceID)
        # request["taskID"] = str(task)
        for seg in range(10):
            time.sleep(soak_t/10)
            prog = seg*10
            print(f"Progress of tray {position}: {prog}")
            self.update_state(state='PROGRESS', meta={'Percent': prog, 'Task' : 'Watering'})
        self.update_state(state='PROGRESS', meta={'Percent': prog, 'Task' : 'Draining'})
        print(f"Activating Pump {position} for draining")
        utray.drain_tray(time=5)
        notify = req.put(f'http://localhost:5000/drainDone/{deviceID}', json={'Task' : True})
    except Exception as e:
        print("Error caught during task")
        print(e.message, e.args)
    finally:
        pass
        # Cleanup
        # Ensure pump is turned off
        # lower_tray.mainPump_off()
        # print(json.dumps(request))
        # with app.app_context():
        #         tresp = req.put("https://192.168.1.75:3000/tray/receive_taskID", verify=False , json=request )

@app.route('/water_plant', methods=['POST'])
def water_plant():
    resp = jsonify({"Ack" : False})
    if request.method == 'POST':
        tray_req = request.get_json()
        deviceID = tray_req["deviceID"]
        try:
            # check taskid if tray is already in service RETURN ERR
            if deviceID not in registry.keys() or registry[deviceID][1]:
                raise Exception
            #fill_queue.put(deviceID)
            task = servceTray(deviceID,registry[deviceID][0])
            # fill_queue.enqueue_call(func=service_Tray, args=(deviceID,))
            registry.get(deviceID)[1] = True
            GPIO.output(systemLED, GPIO.HIGH)
            resp = jsonify({"Ack" : True})
        except Exception as err:
            print("Error occurred while trying to add task to queue")
            # print(err.message, err.args)
            GPIO.output(systemLED, GPIO.LOW)
            # Create other exceptions for specific cases
    return resp

# def sched_water(deviceID):
#     try:
#         # check taskid if tray is already in service RETURN ERR
#         if deviceID not in registry.keys() or registry[deviceID][1]:
#             raise Exception
#         #fill_queue.put(deviceID)
#         print('break1')
#         # fill_queue.enqueue_call(func=service_Tray, args=(deviceID,))
#         registry.get(deviceID)[1] = True
#         GPIO.output(systemLED, GPIO.HIGH)
#     except Exception as err:
#         print("Error occurred while trying to add task to queue")
#         # print(err.message, err.args)
#         GPIO.output(systemLED, GPIO.LOW)
#         # Create other exceptions for specific cases

"""
Status Functions
"""
@app.route('/')
def index():
    resp = {**sys_info, **registry}
    return str(resp)
    # return 'Plant Queue: ' + str(plant_queue)

@app.route('/drainDone/<deviceID>', methods=['PUT'])
def drainDone(deviceID):
    resp = jsonify({'Ack' : True})
    print(f"Notify Server task is done for: {deviceID}")
    request = { "systemID" : systemID,
            "deviceID": deviceID,
            "status" : False
            }
    if deviceID in registry.keys():
        registry[deviceID][1] = False
    else:
        # Notify Device is not in registry
        print(1)
    with app.app_context():
        tresp = req.put("https://192.168.1.75:3000/tray/receive_taskID", verify=False , json=request )
    print(tresp)
    inserv = [ x[1] for _, x in registry.items() ]
    if True not in inserv:
        GPIO.output(systemLED, GPIO.LOW)
    return resp

@app.route('/tray_status/<task_id>', methods=['GET'])
def tray_status(task_id):
    task = drainStart.AsyncResult(task_id)
    resp = {"Ack" : False, "task_status" : task}
    ### TO-DO ###
    return resp

"""
Registration Functions
"""
####### MAIN TO-DO #########
@app.route('/register_tray', methods=['POST'])
def register_tray():
    # Place holder function
    resp = jsonify({"Ack": False})
    if request.method == 'POST':
        tray = request.get_json()
        deviceID = tray['deviceID']
        if deviceID in registry.keys():
            # Device already registered 
            ### TO-DO ###
            return resp
        registry[deviceID] = [tray['position'], False]
        trays[tray['position']].register_tray(deviceID)
        resp = jsonify({'Ack': True})
    return resp

@app.route('/unregister_tray', methods=['POST'])
def unregister_tray():
    resp = jsonify({'Ack' : False})
    if request.method == 'POST':
        tray = request.get_json()
        deviceID = tray['deviceID']
        if deviceID not in registry.keys():
            print("DeviceID Not Registered in System")
            return resp 
        if registry.get(deviceID)[1]:
            # Device is in operation. Please wait till tray is completes job cycle
            print("Upper tray is currently running a task")
            ### TO-DO ###
            return resp
        position = registry[deviceID][0]
        registry.pop(deviceID)
        trays[position].unregister_tray()
        resp = jsonify({'Ack' : True})
    return resp


"""
Main Function
"""
#Synchronize function with web application
### To-Do ###
def sync_app(systemID):
    print("This function does nothing right now")
    sys_req = jsonify({'systemID': systemID})
    resp = req.get('<<Sync Function URL>>', json=sys_req)
    # Update lower tray information
    # Update registry

def main():
    signal.signal(signal.SIGINT, quit_Greg)
    try:
        #threading.Thread(target=service_Tray,args=(fill_queue,), daemon=True).start()
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        print("Shutting Down")
        quit_Greg()
    finally:
        print('Cleanup')
        GPIO.output(systemLED, GPIO.LOW)

if __name__ == '__main__':
    main()
