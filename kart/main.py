# import can
from time import sleep
import struct
import sys
import cv2
import logging
# import steer as kart, brake as kart, motor as kart # this does not work
# or i can do this
# import steer as SteerManager, brake as BrakeManager, motor as MotorManager

from statemachine.statemachine import MasterStateManager
from linedetection.linedetection import process_frame
from objectdetection.objectdetection import detect_objects

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Variables
angle_left = -1.25
angle_center = 0.0
angle_right = 1.25
max_speed = 100
min_speed = 0

camera_path = 0

# Frame processing variables
frame_count = 0
object_detection_interval = 5
last_detections = []

# change the interface to virtual for testing
# change the interface to socketcan and can0 for real testing
def initialize_can():
    bus = can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    return bus

def send_test_message(bus):
    message = can.Message(arbitration_id=0x220, data=[1, 2, 3, 4, 5, 6, 7, 8], is_extended_id=False)
    bus.send(message)
    print("Sent test message!")



def main(source: str, is_camera: bool = False):
    """
    Orchestrates lane detection and object detection using either a video file or camera.
    Args:
        source: path to video file or camera index as string
        is_camera: set True to treat source as camera index
    """
    # Initialize state manager
    state_manager = MasterStateManager()

    # Initialize capture (camera or video file)
    if is_camera:
        cap = cv2.VideoCapture(int(source))
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: Could not open {'camera' if is_camera else 'video file'}: {source}")
        return

    global frame_count, last_detections

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # ---- Lane Detection ----
            steering_cmd, lane_debug = process_frame(frame)
            combined_frame = lane_debug.copy()

            # ---- Object Detection ----
            # Object detection less frequently
            if frame_count % object_detection_interval == 0:
                detections = detect_objects(frame)
                last_detections = detections
            else:
                detections = last_detections

            # Detect zebra crossing
            zebra = [(label, conf) for label, conf in detections if label == 'zebra-crossing']
            detection_label, confidence = zebra[0] if zebra else (None, 0.0)

            # Draw object detections
            for det in detections:
                if len(det) == 3:
                    label, conf, bbox = det
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(combined_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(combined_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    label, conf = det
                    cv2.putText(combined_frame, f"{label} {conf:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


            # ---- State Update ----
            state_info = state_manager.update_states(steering_cmd, detection_label, confidence)
            lane_state = state_info['lane_state']
            override = state_info.get('override', False)
            logging.info(f"Lane: {lane_state}, Override: {override}")

            # ---- Visualization ----

            cv2.imshow("Combined View", combined_frame)

            # overlay lane_debug and detection boxes
            # cv2.imshow('Lane', lane_debug)
            # # You can also draw detections on frame and show:
            # # for label, conf in detections: ... cv2.rectangle, putText, etc.
            # cv2.imshow('Frame', frame)

            # ---- Actions ----
            if override:
                logging.warning("Action: BRAKE (zebra crossing)")
            else:
                match lane_state:
                    case 'turning_left':
                        logging.info('Action: Steering Left')
                    case 'turning_right':
                        logging.info('Action: Steering Right')
                    case 'driving_straight':
                        logging.info('Action: Moving Forward')
                    case _:
                        logging.info('Action: Searching for Lane')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # Usage:
    #   python main.py <video_path>
    #   python main.py <camera_index> --camera
    import argparse
    parser = argparse.ArgumentParser(description='Run lane and object detection')
    parser.add_argument('source', help='Video file path or camera index')
    parser.add_argument('--camera', action='store_true', help='Use camera')
    args = parser.parse_args()
    main(args.source, is_camera=args.camera)


# def main():
#     # bus = initialize_can() # call function to intialize the can
#     bus = initialize_can() # call function to intialize the can
#     bus.shutdown() # shutdown the bus

#     # convert_to_ieee754(-1.0) # call function to convert to ieee754
