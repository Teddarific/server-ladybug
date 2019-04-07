from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_socketio import SocketIO, send, emit
from time import sleep
import random
from scrape import recieve_front_end_link

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('new connection!')

@socketio.on('init')
def handle_init(data):
    if "feLink" in data:
        recieve_front_end_link(data["feLink"], socketio)

@socketio.on('test')
def handle_test(data):
    if "feLink" in data:
        print(data["feLink"])

    if "beLink" in data:
        print(data["beLink"])

    testData = [
        {
            "severity": "success",
            "text": "Success! Accessibility checks passed."
        },
        {
            "severity": "warning",
            "text": "Too much text was found on https://www.alexanderdanilowicz.com"
        },
        {
            "severity": "error",
            "text": "Found a broken button on https://www.alexanderdanilowicz.com"
        },
        {
            "severity": "warning",
            "text": "Color scheme is not color blind friendly"
        },
        {
            "severity": "error",
            "text": "Broken images were found on https://www.alexanderdanilowicz.com"
        }
    ]

    isInfo = True
    while True:
        if isInfo:
            selected =  {
                        "severity": "info",
                        "text": "Starting analysis on too much text..."
                    }
            isInfo = False
        else:
            selected = random.choice(testData)
            isInfo = True

        socketio.emit('data', selected)
        sleep(1)



if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=5000, debug=True)
