#!flask/bin/python
from flask import Flask, jsonify, render_template, request

import json
import random
import time
import datetime
import threading
import webbrowser

app = Flask(__name__)

PORT = 5000 + random.randint(0, 999)

DATA_TABLE = 'data/status.txt'

LONG_POLL_DELAY = 5 # seconds

@app.route('/')
def index():
    """
    Main web site entry point.
    """
    return render_template("index.html", port=PORT)
    #    return "MTA delays!"

@app.route('/data', methods=['GET'])
def get_data():
    with open(DATA_TABLE) as json_file:
        data = json.load(json_file)
    
    clean_data = {}
    for line in data:
        if data[line].lower() == "delays":
            clean_data[line] = "delayed"
        else:
            clean_data[line] = "not delayed"

    
    now = datetime.datetime.now()

    info = {'time_loaded': str(now),
            'status': json.dumps(clean_data)
    }
    # print(info)
    return jsonify(info)

@app.route('/status/<string:line_name>', methods=['GET'])
def get_status(line_name):
    with open(DATA_TABLE) as json_file:
        data = json.load(json_file)

    if line_name not in data:
        return "Invalid line"
    elif data[line_name].lower() == "delays":
        return "Delays"
    else:
        return "No delays"

@app.route('/uptime/<string:line_name>', methods=['GET'])
def get_uptime(line_name):
    return line_name


@app.route("/updated")
def updated():
    """
    Wait until something has changed, and report it. 
    """
    while not app.config['updated']:
        time.sleep(0.5)
    app.config['updated'] = False    # it'll be reported by return, so turn off signal
    return "changed!"

def long_poll_update(first_time=False):
    """
        Server long-polling the data "occasionally" for updates for the client. 
        The first time it's run (presumably synchronously with the main program), 
        it just kicks off an asynchronous Timer. Subsequent invocations (via Timer)
        actually signal an update is ready.
    """
    app.config['updated'] = not first_time
    threading.Timer(LONG_POLL_DELAY, long_poll_update).start()

if __name__ == '__main__':
    # start occasional update simulation
    long_poll_update(first_time=True)

    # start server and web page pointing to it
    url = "http://127.0.0.1:{}".format(PORT)
    wb = webbrowser.get(None)  # instead of None, can be "firefox" etc
    threading.Timer(1.25, lambda: wb.open(url) ).start()
    app.run(port=PORT, debug=False)
