# --- main.py ---
import argparse
import logging
import cv2
import can

from time import sleep
from movement.motor import forward_message # Function
from movement.steer import steer_message # Function
from movement.brake import set_brake_force_message # Function
from linedetection.linedetection import process_frame # Function
from objectdetection.objecttest import detect_objects # Function
from carcontroller import CarController # Class
from statemachine.master_state_manager import MasterStateManager # Class


DEBUG_MODE = True
SHOW_VIDEO = True
DISABLE_OBJECT_DETECTION = False
DISABLE_LANE_DETECTION = False
LOG_MODE = True

size_scale = 0.6 if DEBUG_MODE else 1.0
frame_skip = 10
object_detection_interval = 5
no_crossing_person_threshold = 50

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def initialize_can():
    if DEBUG_MODE:
        return can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    else:
        return can.Bus(interface='socketcan', channel='can0', bitrate=500000)

def main(source: str, is_camera: bool = False):
    bus = initialize_can()
    controller = CarController(bus, debug=DEBUG_MODE)
    state_manager = MasterStateManager()

    cap = cv2.VideoCapture(int(source) if is_camera else source)
    if not cap.isOpened():
        print(f"Error: Could not open {'camera' if is_camera else 'video file'}: {source}")
        return

    frame_count = 0
    no_crossing_person = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            small_frame = cv2.resize(frame, (0, 0), fx=size_scale, fy=size_scale)
            steering_cmd, lane_debug = None, None
            if not DISABLE_LANE_DETECTION:
                steering_cmd, lane_debug = process_frame(small_frame.copy())
                combined_frame = lane_debug.copy()
            else:
                combined_frame = small_frame.copy()

            manbox_position = []
            crossbox_position = []
            detected_red = False
            detected_green = False

            if not DISABLE_OBJECT_DETECTION and frame_count % object_detection_interval == 0:
                detections = detect_objects(small_frame, size_scale)
                for label, conf, (x1, y1), (x2, y2) in detections:
                    logging.info(f"OBJECT: {label} | coords: ({x1},{y1}), ({x2},{y2})")
                    cv2.rectangle(combined_frame, (x1, y1), (x2, y2), (0, 50, 150), 2)
                    cv2.putText(combined_frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 150), 2)

                    if label == 'zebra-crossing':
                        crossbox_position = [x1, y1, x2, y2]
                    elif label == 'person':
                        manbox_position = [x1, y1, x2, y2]
                    elif label == 'traffic-light-red':
                        detected_red = True
                    elif label == 'traffic-light-green':
                        detected_green = True

                if not manbox_position or not crossbox_position or state_manager.crossed():
                    no_crossing_person += 1
                else:
                    no_crossing_person = 0

            if SHOW_VIDEO:
                cv2.imshow("Combined View", combined_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            state_info = state_manager.update(
                steering_cmd, 
                manbox_position, 
                crossbox_position, 
                detected_red, 
                detected_green
            )

            lane_state_obj = state_info['lane_state']
            override = state_info['override']

            if no_crossing_person > no_crossing_person_threshold:
                state_manager.reset_crossing()

            logging.info(f"Lane: {lane_state_obj.__class__.__name__}, Override: {override}")
            logging.info(f"Crossing State: {state_manager.cross_manager.state}")
            logging.info(f"Traffic Light State: {state_manager.traffic_manager.state}")

            if override:
                logging.warning(f"Override triggered: {override}")
                controller.stop()
            else:
                lane_state_obj.act(controller)

    finally:
        controller.steer(0.0)
        cap.release()
        cv2.destroyAllWindows()
        bus.shutdown()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run lane and object detection')
    parser.add_argument('source', help='Video file path or camera index')
    parser.add_argument('--camera', action='store_true', help='Use camera')
    args = parser.parse_args()
    main(args.source, is_camera=args.camera)
