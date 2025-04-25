# objectdetection.py
"""
Wrapper for YOLO-based object detection using an OpenVINO-exported model.
Provides a frame-level `detect_objects(frame)` function that returns detections.
"""
from ultralytics import YOLO
import numpy as np

# Load the exported OpenVINO model once
model = YOLO('./objectdetection/newbest.pt')

model.export(format='openvino') # export in openvino format
ov_model = YOLO('./objectdetection/newbest_openvino_model/') # load the exported openvino model

# You can adjust this threshold or pass it as a parameter
CONFIDENCE_THRESHOLD = 0.5

# Confidence threshold for filtering detections
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

    # Extract boxes, class ids, confidences
    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        if conf < CONFIDENCE_THRESHOLD:
            continue

        label = f'{model.names[cls]} {conf:.2f}'
        detections.append((label, conf))

    return detections