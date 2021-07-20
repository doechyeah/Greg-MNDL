from flask import Flask, jsonify, request
from celery import Celery
# import psutil
# import datetime
import os, time, json
import requests as req

app = Flask(__name__)

# celery = Celery(app.name, broker='redis://localhost:6379/0')
# start celery work with and redis
# $ redis-server
# $ celery -A <Application Name>.celery worker -l info

plant_queue = {}

# Load System Information.
with open('operationbox/system_info.json') as f:
    sys_info = json.loads(f.read())


# This task will find the plant that needs to be watered and send an update post request to the web application
# @celery.task
# def add_plant(plantname, position, potsize, soilcomp):
#     time.sleep(10)
#     waterL = potsize*2.5/7*soilcomp
#     print(plantname, position, waterL)
#     r = req.post('https://<<<<NODEJSserver>>>>/plant_task_update/<<<Include plant info and photo>>>)

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
        new_plant =  request.get_json()
        poisition = sys_info["mapping"][new_plant["sensorID"]]
        plant_queue[new_plant["sensorID"]] = [position, new_plant["potsize"], new_plant["soilcomp"]]
        #add_plant.apply_async(args[new_plant["sensorID"], position, new_plant["potsize"], new_plant["soilcomp"]])
        print("Added plant to queue")
        resp = jsonify({"Ack" : True})
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
