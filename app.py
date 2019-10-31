#!flask/bin/python
from flask import Flask, jsonify, render_template, request

import datetime
from google.transit import gtfs_realtime_pb2
import json
import random
import requests
import time
import threading
import webbrowser

from src.mta_line import MTALine

app = Flask(__name__)

PORT = 5000 + random.randint(0, 999)

DATA_TABLE = 'data/status.txt'
UPDATE_FREQUENCY = 10 # seconds

# TODO Move to config
MTA_API_KEY = "395ab01a597dfcd0db4b8061d0ee6821"
# We pull the following MTA feed
FEED_URL = "http://datamine.mta.info/mta_esi.php?key={}&feed_id=1".format(MTA_API_KEY)
# This feed supports the following lines
SUPPORTED_LINES = ["1", "2", "3", "4", "5", "6", "S"]
CURRENT_STATUS = {}

@app.route('/')
def index():
    """
    Main web site entry point.
    """
    return render_template("index.html", port=PORT)
    #    return "MTA delays!"

@app.route('/data', methods=['GET'])
def get_data():
    # _poll_api_data()
    _poll_local_data()

    data = {}
    for mta_line in CURRENT_STATUS:
        data[mta_line] = CURRENT_STATUS[mta_line].current_status
    
    now = datetime.datetime.now()

    info = {'time_loaded': str(now),
            'status': json.dumps(data)
    }
    # print(info)
    return jsonify(info)

@app.route('/status/<string:line_name>', methods=['GET'])
def get_status(line_name):
    if line_name.upper() not in SUPPORTED_LINES:
        return "Invalid line"
    else:
        return CURRENT_STATUS[line_name.upper()].current_status

@app.route('/uptime/<string:line_name>', methods=['GET'])
def get_uptime(line_name):
    if line_name.upper() not in SUPPORTED_LINES:
        return "Invalid line"
    else:
        return CURRENT_STATUS[line_name.upper()].get_uptime()


@app.route("/updated")
def updated():
    """
    Wait until something has changed, and report it. 
    """
    while not app.config['updated']:
        time.sleep(0.5)
    app.config['updated'] = False    # it'll be reported by return, so turn off signal
    return "changed!"

def _poll_local_data():
    """
    Poll data from data source and update current data.
    This pulls from a text file residing locally on the server.
    It was used for testing the app outside of the MTA API.
    """
    with open(DATA_TABLE) as json_file:
        data = json.load(json_file)

    for line in data:
        if line not in CURRENT_STATUS:
            CURRENT_STATUS[line.upper()] = MTALine(line.upper())
        else:
            changed = CURRENT_STATUS[line.upper()].update_status(data[line])
            if changed:
                app.config['updated'] = True
    
    threading.Timer(UPDATE_FREQUENCY, _poll_local_data).start()


def _poll_api_data():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(FEED_URL, allow_redirects=True)
    feed.ParseFromString(response.content)
    """
    An alert entity in the feed will look like this:
    id: "000349"
    alert {
        informed_entity {
            trip {
            trip_id: "085550_5..S03R"
            route_id: "5"
            }
        }
        header_text {
            translation {
            text: "Train delayed"
            }
        }
    }
    """
    alerts = [e for e in feed.entity if e.HasField('alert')]  

    current_delays = set()
    # parse alerts
    for alert in alerts:
        for alert_message in alert.alert.header_text.translation:
            if "Train delayed" in alert_message.text:
                for informed_entity in alert.alert.informed_entity:
                    if informed_entity.HasField('trip'):
                        current_delays.add(informed_entity.trip.route_id)
    
    for line in CURRENT_STATUS:
        if line in current_delays:
            changed = CURRENT_STATUS[line].update_status('delayed')
        else:
            changed = CURRENT_STATUS[line].update_status('ok')
        if changed:
            app.config['updated'] = True
    
    threading.Timer(UPDATE_FREQUENCY, _poll_api_data).start()


if __name__ == '__main__':
    # intialize all the supported lines
    for line in SUPPORTED_LINES:
        CURRENT_STATUS[line] = MTALine(line)

    # start long polling
    app.config['updated'] = False
    _poll_api_data()
    # _poll_local_data()


    # start server and web page pointing to it
    url = "http://127.0.0.1:{}".format(PORT)
    wb = webbrowser.get(None)  # instead of None, can be "firefox" etc
    threading.Timer(1.25, lambda: wb.open(url) ).start()
    app.run(port=PORT, debug=False)
