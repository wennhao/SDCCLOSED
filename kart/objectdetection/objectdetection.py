from ultralytics import YOLO
import cv2
import numpy as np

detected_objects = {
    "car": 0,
    "one-way-left": 0,
    "sign-left-only": 0,
    "speed-sign-20": 0, 
    "speed-sign-30": 0,
    "stop-sign": 0,
    "traffic-light-green": 0,
    "traffic-light-red": 0,
    "traffic-light-off": 0,
    "zebra-crossing": 0,
    "person": 0
}
objects_size = {
    "car": 7000,
    "one-way-left": 900,
    "sign-left-only": 1200,
    "speed-sign-20": 1500, 
    "speed-sign-30": 1000,
    "stop-sign": 1800,
    "traffic-light-green": 900,
    "traffic-light-red": 900,
    "traffic-light-off": 900,
    "zebra-crossing": 4500,
    "person": 4500
}

frame_pool = 10
frame_threshold = 1
current_frame = 0

# model = YOLO('ultra_object_detector_3000.pt')

# model.export(format='openvino') # export in openvino format
ov_model = YOLO('objectdetection/ultra_object_detector_3000_openvino_model/') # load the exported openvino model

# path_to_video = 'imgtovid/recording 03-04-2025 15-51-02/output_video.mp4'
# path_to_camera = 0

# cam = cv2.VideoCapture(path_to_video)

def detect_objects(frame, scale):
    try:
        current_frame
    except NameError:
        current_frame = 0

    if current_frame >= frame_pool:
        current_frame = 0
        for key in detected_objects:
            detected_objects[key] = 0

    ### OBJECT DETECTION
    results = ov_model(frame)
    boxes = results[0].boxes
    detections = []

    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        if conf >= 0.5:
            # Check if label exists in detected_objects
            if ov_model.names[cls] in detected_objects:
                # If object has a valid class, add count
                key = ov_model.names[cls]
                detected_objects[key] += 1
                if detected_objects[key] >= frame_threshold and (abs(x1-x2)*abs(y1-y2)) >= (objects_size[key]*scale):
                    detected_objects[key] = 0
                    detections.append((key, conf, (x1, y1), (x2, y2)))
                    # Display
                    # label = f'{key} {conf:.2f}'
                    # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 50, 150), 3)
                    # cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 150), 3)
                # else:
                    # Display
                    # label = f'{ov_model.names[cls]} {conf:.2f}'
                #     cv2.rectangle(frame, (x1, y1), (x2, y2), (240, 50, 0), 2)
                #     cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 50, 0), 2)
                # cv2.putText(frame, str(abs(x1-x2)*abs(y1-y2)), (x1+50, y1+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 0, 250), 2)
                current_frame += 1
    # cv2.imshow('Camera', frame)
    return detections

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
person
'''