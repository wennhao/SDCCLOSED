from ultralytics import YOLO
import cv2
import numpy as np
from roboflow import Roboflow

detected_objects = [
    {"class": "car", "count": 0},
    {"class": "one-way-left", "count": 0},
    {"class": "sign-left-only", "count": 0},
    {"class": "speed-sign-20", "count": 0}, 
    {"class": "speed-sign-30", "count": 0},
    {"class": "stop-sign", "count": 0},
    {"class": "traffic-light-green", "count": 0},
    {"class": "traffic-light-red", "count": 0},
    {"class": "traffic-light-off", "count": 0},
    {"class": "zebra-crossing", "count": 0}
]

frame_pool = 6
frame_threshold = 3
current_frame = 0

model = YOLO('newbest.pt')

model.export(format='openvino') # export in openvino format
ov_model = YOLO('newbest_openvino_model/') # load the exported openvino model

path_to_camera = 0

cam = cv2.VideoCapture(path_to_camera)
ret, frame = cam.read()

def execute(object_class):
    if object_class == "car":
        print(object_class)
    elif object_class == "one-way-left":
        print(object_class)
    elif object_class == "sign-left-only":
        print(object_class)
    elif object_class == "speed-sign-20":
        print(object_class)
    elif object_class == "speed-sign-30":
        print(object_class)
    elif object_class == "stop-sign":
        print(object_class)
    elif object_class == "traffic-light-green":
        print(object_class)
    elif object_class == "traffic-light-red":
        print(object_class)
    elif object_class == "zebra-crossing":
        print(object_class)
    else:
        print("not a valid class")
    # ...

while ret:
    ret, frame = cam.read()
    if not ret:
        break

    if current_frame >= frame_pool:
        current_frame = 0
        for obj in detected_objects:
            obj["count"] = 0

    ### OBJECT DETECTION
    results = ov_model(frame)
    boxes = results[0].boxes

    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        if conf >= 0.5:
            # Check if label exists in detected_objects
            for obj in detected_objects:
                if obj["class"] == model.names[cls]:
                    # If object has a valid class, add count
                    obj["count"] += 1
                    if obj["count"] >= frame_threshold:
                        execute(obj["class"])
                        obj["count"] = 0
                    break

            # Display
            label = f'{model.names[cls]} {conf:.2f}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    cv2.imshow('Camera', frame)

    current_frame += 1

    if cv2.waitKey(1) == ord('q'):
        break

'''
classes:
------------
car
one-way-left
sign-left-only
speed-sign-20
speed-sign-30
stop-sign
traffic-light-green
traffic-light-red
traffic-light-off (niet gebruikt)
zebra-crossing
'''