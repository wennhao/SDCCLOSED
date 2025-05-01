import can
from time import sleep
import struct
import sys
# import steer as kart, brake as kart, motor as kart # this does not work
# or i can do this
import steer as SteerManager, brake as BrakeManager, motor as MotorManager
from statemachine.statemachine import MasterStateManager
from linedetection.linedetection import process_frame
from objectdetection.objectdetection import detect_objects
import cv2

# Variables
angle_left = -1.25
angle_center = 0.0
angle_right = 1.25
max_speed = 100
min_speed = 0

camera_path = 0


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

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # ---- Lane Detection ----
            steering_cmd, lane_debug = process_frame(frame)

            combined_frame = lane_debug.copy()

            # ---- Object Detection ----
            detections = detect_objects(frame)  # returns list of (label, confidence)
            # Example: pick zebra crossing
            zebra = [(label, conf) for label, conf in detections if label == 'zebra-crossing']
            if zebra:
                detection_label, confidence = zebra[0]
            else:
                detection_label, confidence = None, 0.0

            # Draw object detections on the same frame
            detections = detect_objects(frame)
            for det in detections:
                det.draw(combined_frame, color=(0,255,0))  # green boxes


            # ---- State Update ----
            state_info = state_manager.update_states(steering_cmd, detection_label, confidence)
            lane_state = state_info['lane_state']
            override = state_info.get('override', False)
            print(f"Lane: {lane_state}, Override: {override}")

            # ---- Visualization ----

            cv2.imshow("Combined View", combined_frame)

            # overlay lane_debug and detection boxes
            # cv2.imshow('Lane', lane_debug)
            # # You can also draw detections on frame and show:
            # # for label, conf in detections: ... cv2.rectangle, putText, etc.
            # cv2.imshow('Frame', frame)

            # ---- Actions ----
            if override:
                print("Action: BRAKE (zebra crossing)")
            else:
                match lane_state:
                    case 'turning_left':
                        print('Action: Steering Left')
                    case 'turning_right':
                        print('Action: Steering Right')
                    case 'driving_straight':
                        print('Action: Moving Forward')
                    case _:
                        print('Action: Searching for Lane')

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
