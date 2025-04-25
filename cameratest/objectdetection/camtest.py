from ultralytics import YOLO
import cv2
import numpy as np
from roboflow import Roboflow

model = YOLO('newbest.pt')

model.export(format='openvino') # export in openvino format
ov_model = YOLO('newbest_openvino_model/') # load the exported openvino model

cam = cv2.VideoCapture('imgtovid/output_video.mp4')
ret, frame = cam.read()

while ret:
    ret, frame = cam.read()
    if not ret:
        break

    # reduce quality based on fx and fy
    frame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)

    ### OBJECT DETECTION
    results = ov_model(frame)
    boxes = results[0].boxes

    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        #if model.names[cls] == 'car' and conf >= 0.5:
        if conf >= 0.5:
            label = f'{model.names[cls]} {conf:.2f}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) == ord('q'):
        break