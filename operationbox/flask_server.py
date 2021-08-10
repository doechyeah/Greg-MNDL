# from logging import raiseExceptions
from flask import Flask, jsonify, request
import threading, os, time, json, signal #, queue
import requests as req
import RPi.GPIO as GPIO
import system_main as sm
from celery import Celery

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
GPIO.setup(sm.systemLED, GPIO.OUT)

registry = dict()

# Cleanup Signal
def quit_Greg(*args):
    print('Stopping Greg System')
    # Turn off LED here
    exit(0)

"""
Service Functions
"""
@celery.task(bind=True)
def drainStart(self, tray, deviceID, soak_t=6):
    for seg in range(10):
        time.sleep(soak_t/10)
        prog = seg*10
        print(f"Progress of tray {tray+1}: {prog}")
        self.update_state(state='PROGRESS', meta={'Percent': prog, 'Task' : 'Watering'})
    self.update_state(state='PROGRESS', meta={'Percent': prog, 'Task' : 'Draining'})
    print(f"Activating Pump {tray} for draining")
    res = sm.trays[tray].drain_tray(time=5)
    notify = req.put(f'http://localhost:5000/drainDone/{deviceID}', json={'Task' : True})
    print(notify)

@app.route('/startdrain', methods=['PUT'])
def start_drain():
    resp = jsonify({"Ack" : False})
    if request.method == 'PUT':
        tray_req = request.get_json()
        position = tray_req["position"]
        devID = tray_req["deviceID"]
        task = drainStart.delay(position, devID)
        requ = {"systemID" : sm.systemID,
                "deviceID" : devID,
                "taskID" : task.id,
		        "status" : True}
        resp = jsonify({"Ack" : True})
    with app.app_context():
        req.put("https://192.168.1.75:3000/tray/receive_taskID", verify=False , json=requ )
    return resp

@app.route('/water_plant', methods=['POST'])
def water_plant():
    resp = jsonify({"Ack" : False})
    if request.method == 'POST':
        tray_req = request.get_json()
        deviceID = tray_req["deviceID"]
        sched_water(deviceID)
        resp = jsonify({"Ack" : True})
    return resp

def sched_water(deviceID):
    #try:
    # check taskid if tray is already in service RETURN ERR
    if deviceID not in registry.keys() or registry[deviceID][1]:
        raise Exception
    #fill_queue.put(deviceID)
    print('break1')
    position = registry[deviceID][0]
    sm.fill_queue.enqueue(sm.service_Tray, args=(deviceID,position,))
    registry.get(deviceID)[1] = True
    # print(f"Size of Fill Queue: {fill_queue.qsize()}")
    GPIO.output(sm.systemLED, GPIO.HIGH)
    #except Exception as err:
    print("Error occurred while trying to add task to queue")
    # print(err.message, err.args)
    GPIO.output(sm.systemLED, GPIO.LOW)
    # Create other exceptions for specific cases

"""
Status Functions
"""
@app.route('/')
def index():
    resp = {**sm.sys_info, **registry}
    return str(resp)
    # return 'Plant Queue: ' + str(plant_queue)

@app.route('/drainDone/<deviceID>', methods=['PUT'])
def drainDone(deviceID):
    resp = jsonify({'Ack' : True})
    print(f"Notify Server task is done for: {deviceID}")
    request = { "systemID" : sm.systemID,
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
        GPIO.output(sm.systemLED, GPIO.LOW)
    return resp

@app.route('/tray_status/<task_id>', methods=['GET'])
def tray_status(task_id):
    task = sm.drainStart.AsyncResult(task_id)
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
        sm.trays[tray['position']].register_tray(deviceID)
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
        sm.trays[position].unregister_tray()
        resp = jsonify({'Ack' : True})
    return resp


"""
Main Function
"""
#Synchronize function with web application
### To-Do ###
# def sync_app(systemID):
#     print("This function does nothing right now")
#     sys_req = jsonify({'systemID': systemID})
#     resp = req.get('<<Sync Function URL>>', json=sys_req)
#     # Update lower tray information
#     # Update registry

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
        GPIO.output(sm.systemLED, GPIO.LOW)

if __name__ == '__main__':
    main()
