# import can
from time import sleep
from motor import forward_message
from steer import steer_message
import struct
import sys
import cv2
import logging
import can
# import steer as kart, brake as kart, motor as kart # this does not work
# or i can do this
# import steer as SteerManager, brake as BrakeManager, motor as MotorManager

from statemachine.statemachine import MasterStateManager, LaneState, TrafficLightState
from linedetection.linedetection import process_frame
#from objectdetection.objectdetection import detect_objects
from objectdetection.objecttest import detect_objects

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

DEBUG_MODE = True
SHOW_VIDEO = True
DISABLE_OBJECT_DETECTION = False
DISABLE_LANE_DETECTION = True

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

frame_skip = 10


# change the interface to virtual for testing
# change the interface to socketcan and can0 for real testing
def initialize_can():
    if DEBUG_MODE:
        # Virtual CAN for simulation/testing
        bus = can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    else:
        # Real CAN for kart control
        bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
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
    bus = initialize_can()

    # Initialize capture (camera or video file)
    if is_camera:
        cap = cv2.VideoCapture(int(source))
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: Could not open {'camera' if is_camera else 'video file'}: {source}")
        return

    global frame_count, last_detections
    size_scale = 0.2

    try:
        while True:
            ret, frame = cap.read()
            small_frame = cv2.resize(frame, (0, 0), fx=size_scale, fy=size_scale)

            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue  # Skip this frame

            


            # ---- Lane Detection ----
            steering_cmd, lane_debug = None, None

            if not DISABLE_LANE_DETECTION:
                steering_cmd, lane_debug = process_frame(small_frame)
                combined_frame = lane_debug.copy()
            else:
                combined_frame = small_frame.copy()

            # ---- Object Detection ----
            # Object detection less frequently
            # ---- Object Detection (Skipped for Testing) ----
            detection_label, confidence, detection_color = None, 0.0, None
            detections = []

            if not DISABLE_OBJECT_DETECTION and frame_count % object_detection_interval == 0:
                detections = detect_objects(small_frame, size_scale)
                for (detection, label, (x1, y1), (x2, y2)) in detections:
                    logging.info(f"OBJECT: {detection}")
                    cv2.rectangle(combined_frame, (x1, y1), (x2, y2), (0, 50, 150), 2)
                    cv2.putText(combined_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 150), 2)

            # ---- Display Debug Information ----        
            if SHOW_VIDEO:
                cv2.imshow("Combined View", combined_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # ---- State Update ----
            state_info = state_manager.update_states(
                steering_cmd, 
                detection_label, 
                confidence,
                detection_color
            )
            lane_state = state_info['lane_state']
            traffic_state = state_info['traffic_state']
            override = state_info['override']

            logging.info(f"Lane: {lane_state}, Override: {override}")


            # ---- Actions / CAN messages ----
            if override:
                logging.warning("BRAKE: zebra crossing")
                if not DEBUG_MODE:
                    bus.send(forward_message(0))
            else:
                match traffic_state:
                    case TrafficLightState.RED:
                        logging.warning("RED light → brake")
                        if not DEBUG_MODE:
                            bus.send(forward_message(0))

                    case TrafficLightState.GREEN:
                        logging.info("GREEN light → go")
                        if not DEBUG_MODE:
                            bus.send(steer_message(angle_center))
                            bus.send(forward_message(60))

                    case _:
                        # No active traffic light: fall back to lane state
                        match lane_state:
                            case LaneState.LEFT:
                                logging.info("Steer Left")
                                if not DEBUG_MODE:
                                    bus.send(steer_message(angle_left))
                                    bus.send(forward_message(30))

                            case LaneState.RIGHT:
                                logging.info("Steer Right")
                                if not DEBUG_MODE:
                                    bus.send(steer_message(angle_right))
                                    bus.send(forward_message(30))

                            case LaneState.STRAIGHT:
                                logging.info("Go Straight")
                                if not DEBUG_MODE:
                                    bus.send(steer_message(angle_center))
                                    bus.send(forward_message(60))

                            case _:
                                logging.info("Searching for Lane")
                                if not DEBUG_MODE:
                                    bus.send(steer_message(angle_center))
                                    bus.send(forward_message(0))


    finally:
        cap.release()
        cv2.destroyAllWindows()
        bus.shutdown()


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
