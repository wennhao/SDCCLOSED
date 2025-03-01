from flask import Flask, render_template, jsonify, Response
import time
import threading
import json
import cv2
import numpy as np
from datetime import datetime

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


# Generate camera feed
def generate_camera_frame():
    # Create a road scene with fixed elements
    frame = np.zeros((600, 800, 3), dtype=np.uint8)  # Larger frame

    # Road (dark gray)
    cv2.rectangle(frame, (0, 300), (800, 600), (80, 80, 80), -1)
    
    # Road markings (white lines)
    for i in range(0, 800, 50):
        cv2.rectangle(frame, (i, 400), (i+30, 410), (255, 255, 255), -1)
    
    return frame

def get_camera_frame():
    frame = generate_camera_frame()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()



# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/car_data')
def get_car_data():
    return jsonify(car_data)

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame = get_camera_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)