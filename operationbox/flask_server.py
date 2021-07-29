from logging import raiseExceptions
from flask import Flask, jsonify, request
import threading, queue, os, time, json
from celery import Celery
import requests as req
import uppertray
import lowertray

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


"""
System Infromation and managment objectsj
"""
# Load System Information.
with open('operationbox/system_info.json') as f:
    sys_info = json.loads(f.read())

systemID = sys_info["LowerTray"]["systemID"]
# tray1 = uppertray.UpperTray(sys_info["mapping"]["tray1"])
# tray2 = uppertray.UpperTray(sys_info["mapping"]["tray2"])
# tray3 = uppertray.UpperTray(sys_info["mapping"]["tray3"])
# trays = [tray1, tray2, tray3]
trays = [ uppertray.UpperTray(gpio[0], gpio[1]) for gpio in sys_info["UpperTrayGPIO"].items() ]
lower_tray = lowertray.LowerTray(systemID, sys_info["LowerTray"]["pumpGPIO"])

# Registry keeps track of which deviceID is assigned to which tray
# ex. { "<deviceID>" : [ UpperTrayObject, "<Available for job>"]}
registry = {}
fill_queue = queue.Queue()

"""
Service Functions
"""
@celery.task(bind=True)
def drainStart(tray, deviceID, time=600):
    time.sleep(time)
    res = trays[tray].drain_tray()
    notify = req.put(f'localhost:5000/drainDone/{deviceID}', json={'Task' : True})

# Threaded Queue that services all trays
def service_Tray():
    while True:
        # Threaded operation to check if any tray needs to be filled
        devID = fill_queue.get()
        request = {"systemID" : systemID,
                    "deviceID" : devID, 
                    "taskID" : None}
        try:
            lower_tray.mainPump_on()
            utray = registry.get(devID)[0]
            result = utray[0].fill_tray()
            if result == -1:
                # Error occurred while opening valve
                raise Exception
            
            # Allow pump to run for 50 seconds to be fill tray
            time.sleep(50)
            lower_tray.mainPump_off()
            
            # Launch celery task to handle when to drain the tray
            task = drainStart.apply_async(utray, devID)
            request['taskID'] = task.id
        except:
            print("Error caught during task")
        finally:
            # Cleanup
            # Ensure pump is turned off
            lower_tray.mainPump_off()
            request = req.post("<URL for a web application to send taskID>", json=jsonify(request) )
            fill_queue.task_done()

@app.route('/water_plant', methods=['POST'])
def water_plant():
    resp = jsonify({"Ack" : False})
    try:
        if request.method == 'POST':
            tray_req = request.get_json()
            deviceID = tray_req["deviceID"]
            # check taskid if tray is already in service RETURN ERR
            if registry[deviceID][1]:
                raise Exception
            registry.get(deviceID)[1] = True
            fill_queue.put(deviceID)
            resp = jsonify({"Ack" : True})
    except:
        print("Error occurred while trying to add task to queue")
        # Create other exceptions for specific cases
    finally:
        return resp

"""
Status Functions
"""
@app.route('/')
def index():
    resp = {**sys_info, **registry}
    return resp
    # return 'Plant Queue: ' + str(plant_queue)

@app.route('/draintray/<deviceID>')
def drainDone(deviceID):
    if deviceID in registry.keys():
        registry[deviceID][1] = False
    else:
        # Notify Device is not in registry
        print(1)
        
@app.route('/tray_status/<task_id>', methods=['GET'])
def tray_status(task_id):
    task = drainStart.AsyncResult(task_id)
    resp = jsonify({"Ack" : False})
    if request.method == 'GET':
        tray = request.get_json()
        status = task
    ### TO-DO ###
    return resp

"""
Registration Functions
"""
####### MAIN TO-DO ###########
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
        registry[deviceID] = [trays[tray['position']], False]
        trays[tray['position']].register_tray(deviceID)
        resp = jsonify({'Ack': True})
    return resp

@app.route('/unregister_tray', methods=['PUT'])
def unregister_tray():
    resp = jsonify({'Ack' : False})
    if request.method == 'POST':
        tray = request.get_json()
        deviceID = tray['deviceID']
        if registry.get(deviceID)[1]:
            # Device is in operation. Please wait till tray is completes job cycle
            ### TO-DO ###
            return resp
        registry.pop(deviceID)
        trays[tray['position']].unregister_tray()
        resp = jsonify({'Ack' : True})
    return resp

"""
Main Function
"""
if __name__ == '__main__':
    threading.Thread(target=service_Tray, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')
