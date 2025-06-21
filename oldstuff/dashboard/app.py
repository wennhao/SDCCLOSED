from flask import Flask, render_template, jsonify, Response
import numpy as np
from datetime import datetime
from camera import generate_frames

app = Flask(__name__)

# Fixed data
car_data = {
    "speed": 100.0,
    "steering_angle": 23.1,
    "system_status": "standby",
    "battery": 111,
    "cpu_usage": 11,
    "selfdriving_mode": False,
    "motor_temp": 11,
    "power_usage": 11,
    "system_errors": [],
    "lidar_data": [],
    "detected_objects": [],
}


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7890, debug=True, threaded=True)