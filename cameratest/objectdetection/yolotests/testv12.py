from ultralytics import YOLO
import cv2
import numpy as np

model_name = 'yolo12n'

model = YOLO(model_name+'.pt')

model.export(format='openvino') # export in openvino format
ov_model = YOLO(model_name+'_openvino_model/') # load the exported openvino model

cam = cv2.VideoCapture('objectdettest.mp4')
ret, frame = cam.read()

total_speed = 0
total_frames = 0

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

    total_speed += results[0].speed['preprocess']+results[0].speed['inference']+results[0].speed['postprocess']
    total_frames += 1
    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) == ord('q'):
        break

print('\nmodel:', model_name, '| avg speed:', total_speed/total_frames, '| total frames:', total_frames)