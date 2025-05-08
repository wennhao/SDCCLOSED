"""
Wrapper for YOLO-based object detection using an OpenVINO-exported model.
Provides a frame-level `detect_objects(frame)` function that returns detections.
"""
from ultralytics import YOLO
import numpy as np

# Load the exported OpenVINO model once
# model = YOLO('./objectdetection/newbest.pt')

# model.export(format='openvino') # export in openvino format
ov_model = YOLO('./objectdetection/newbest_openvino_model/') # load the exported openvino model

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
    data = boxes.data.cpu().numpy()

    for x1, y1, x2, y2, conf, cls in data:
        if conf < CONFIDENCE_THRESHOLD:
            continue
        label = ov_model.names[int(cls)]
        detections.append((label, float(conf), (int(x1), int(y1), int(x2), int(y2))))

    return detections