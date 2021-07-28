from flask import Flask, jsonify, request
import threading, queue, os, time, json
from celery import Celery
# import psutil
# import datetime
import requests as req
import uppertray
import lowertray

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# start celery work with and redis
# $ redis-server
# $ celery -A <Application Name>.celery worker -l info

# Load System Information.
with open('operationbox/system_info.json') as f:
    sys_info = json.loads(f.read())

tray1 = uppertray.UpperTray(sys_info["mapping"]["tray1"])
tray2 = uppertray.UpperTray(sys_info["mapping"]["tray2"])
tray3 = uppertray.UpperTray(sys_info["mapping"]["tray3"])
trays = { 1 : [tray1, False],
          2 : [tray2, False],
          3 : [tray3, False] }
lower = lowertray.LowerTray(sys_info["mapping"]["lowertray"])

@celery.task(bind=True)
def drain_Tray(tray, time):
    time.sleep(time)
    trays.get(tray).drain_tray()
    
# This task will find the plant that needs to be watered and send an update post request to the web application
# @celery.task
# def add_plant(plantname, position, potsize, soilcomp):
#     time.sleep(10)
#     waterL = potsize*2.5/7*soilcomp
#     print(plantname, position, waterL)
#     r = req.post('https://<<<<NODEJSserver>>>>/plant_task_update/<<<Include plant info and photo>>>)

fill_queue = queue.Queue()

def service_Tray(tray, time):
    while True:
        #if q.empty continue
        # Perform tray servicing to water plants
        for serv in trays:
        lower.mainPump_on()
        trays.get(tray).fill_tray()
        time.sleep(50)
        lower.mainPump_off()
        drain_Tray(tray, time)

@app.route('/')
def index():
    resp = {**sys_info, **plant_queue}
    return resp
    # return 'Plant Queue: ' + str(plant_queue)

@app.route('/get_queue', methods=['GET'])
def get_queue():
    if methods == 'GET':
        return jsonify(plant_queue)

@app.route('/water_plant', methods=['POST'])
def water_plant():
    resp = jsonify({"Ack" : False})
    if request.method == 'POST':
        tray_req =  request.get_json()
        # check taskid if tray is already in service RETURN ERR
        """TO-DO"""
        ###########
        fill_queue.put(tray_req["deviceID"])
        print("Added plant to queue")
        resp = jsonify({"Ack" : True})
    return resp

@app.route('/register_tray', methods=['POST'])
def reg_tray():
    # Place holder function


if __name__ == '__main__':
    # threading.thread()
    app.run(debug=True, host='0.0.0.0')
