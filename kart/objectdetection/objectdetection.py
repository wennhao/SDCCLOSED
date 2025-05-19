"""
Wrapper for YOLO-based object detection using an OpenVINO-exported model.
Provides a frame-level `detect_objects(frame)` function that returns detections.
"""
from ultralytics import YOLO
import numpy as np

# Load the exported OpenVINO model once
# model = YOLO('./objectdetection/newbest.pt')

# model.export(format='openvino') # export in openvino format
ov_model = YOLO('./objectdetection/withman_openvino_model/') # load the exported openvino model

# You can adjust this threshold or pass it as a parameter
CONFIDENCE_THRESHOLD = 0.5

def detect_objects(frame):
    """
    Detect objects in a single frame.

    Args:
        frame (np.ndarray): BGR image frame from OpenCV.

    Returns:
        List of tuples: [(label: str, confidence: float), ...]
    """
    results = ov_model(frame)
    boxes = results[0].boxes


    detections = []
    for box in results[0].boxes:
        cls     = int(box.cls[0])
        name    = results[0].names[cls]        # e.g. "traffic-light-red"
        conf    = float(box.conf[0])
        bbox    = tuple(map(int, box.xyxy[0])) # (x1,y1,x2,y2)

        if conf < 0.5:
            continue

        # for traffic lights, strip the color into a meta-field
        if name.startswith("traffic-light"):
            # name is e.g. "traffic-light-red" or "traffic-light-green"
            _, _, color = name.partition("-")   # color == "red" or "green"
            detections.append(("traffic_light", conf, bbox, color))
        else:
            # zebra, stop-sign, etc
            detections.append((name, conf, bbox, None))

    return detections