#!flask/bin/python
from flask import Flask, jsonify, render_template, request

import json
import random
import time
import datetime
import threading
import webbrowser

from src.mta_line import MTALine

app = Flask(__name__)

PORT = 5000 + random.randint(0, 999)

DATA_TABLE = 'data/status.txt'
LONG_POLL_DELAY = 5 # seconds
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
    _poll_data()
    
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
    if line_name.upper() not in CURRENT_STATUS:
        return "Invalid line"
    else:
        return CURRENT_STATUS[line_name.upper()].current_status

@app.route('/uptime/<string:line_name>', methods=['GET'])
def get_uptime(line_name):
    if line_name.upper() not in CURRENT_STATUS:
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

def _poll_data():
    """
    Poll data from data source and update current data
    """
    with open(DATA_TABLE) as json_file:
        data = json.load(json_file)

    for line in data:
        if line not in CURRENT_STATUS:
            CURRENT_STATUS[line.upper()] = MTALine(line.upper())
        else:
            CURRENT_STATUS[line.upper()].update_status(data[line])

def _long_poll_update(first_time=False):
    """
    Server long-polling the data "occasionally" for updates for the client. 
    The first time it's run (presumably synchronously with the main program), 
    it just kicks off an asynchronous Timer. Subsequent invocations (via Timer)
    actually signal an update is ready.
    """
    app.config['updated'] = not first_time
    threading.Timer(LONG_POLL_DELAY, _long_poll_update).start()

if __name__ == '__main__':
    # start occasional update simulation
    _long_poll_update(first_time=True)

    # start server and web page pointing to it
    url = "http://127.0.0.1:{}".format(PORT)
    wb = webbrowser.get(None)  # instead of None, can be "firefox" etc
    threading.Timer(1.25, lambda: wb.open(url) ).start()
    app.run(port=PORT, debug=False)
