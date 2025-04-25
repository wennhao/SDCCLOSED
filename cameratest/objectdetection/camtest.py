from ultralytics import YOLO
import cv2
import numpy as np
from roboflow import Roboflow

model = YOLO('newbest.pt')

model.export(format='openvino') # export in openvino format
ov_model = YOLO('newbest_openvino_model/') # load the exported openvino model

path_to_camera = 0

cam = cv2.VideoCapture(path_to_camera)
ret, frame = cam.read()

while ret:
    ret, frame = cam.read()
    if not ret:
        break

    ### OBJECT DETECTION
    results = ov_model(frame)
    boxes = results[0].boxes

    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        if conf >= 0.5:
            # Check objects and execute
            

            # Display
            label = f'{model.names[cls]} {conf:.2f}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    cv2.imshow('Camera', frame)

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