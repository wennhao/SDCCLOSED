import argparse
import logging
import cv2
import can

from time import sleep
from linedetection.linedetection import process_frame # Function
from objectdetection.objectdetection import detect_objects # Function
from carcontroller import CarController # Class
from statemachine.master_state_manager import MasterStateManager # Class

# Lidar
from lidar.lidar_detection import LidarDetector # Class

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Constants
DEBUG_MODE = True
SHOW_VIDEO = False
DISABLE_OBJECT_DETECTION = True
DISABLE_LANE_DETECTION = False
DISABLE_LIDAR = False
LOG_MODE = True
LINUX_MODE = True

lidar_port = '/dev/ttyUSB0' if LINUX_MODE else 'com4' # Adjust port based on OS
# Variables
size_scale = 0.6 if DEBUG_MODE else 1.0
frame_skip = 10
object_detection_interval = 5
no_crossing_person_threshold = 50



def initialize_can():
    if DEBUG_MODE:
        return can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    else:
        return can.Bus(interface='socketcan', channel='can0', bitrate=500000)

def main(source: str, is_camera: bool = False):
    bus = initialize_can()
    controller = CarController(bus, debug=DEBUG_MODE)
    state_manager = MasterStateManager()

    # Initialize Lidar Detector
    lidar_detector = LidarDetector(port=lidar_port, baudrate=115200, timeout=1, front_thresh=500, left_thresh=500, right_thresh=500, debug=DEBUG_MODE)
    lidar_detector.start()  # Start the Lidar thread

    cap = cv2.VideoCapture(int(source) if is_camera else source)
    if not cap.isOpened():
        print(f"Error: Could not open {'camera' if is_camera else 'video file'}: {source}")
        return

    frame_count = 0
    no_crossing_person_counter = 0

    try:
        while True:
            """
            FRAME PROCESSING
            Video Capture setup and frame reading.
            """
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            small_frame = cv2.resize(frame, (0, 0), fx=size_scale, fy=size_scale)
            steering_cmd, lane_debug = None, None
            """
            LIDAR DETECTION
            This section checks the Lidar for obstacles and updates the state manager accordingly.
            """
            if not DISABLE_LIDAR:
                front_obs, left_obs, right_obs = lidar_detector.get_obstacles()

                if front_obs:
                    logging.warning("LIDAR: Obstacle detected in front!")
                    override = True
                    controller.stop()
            """
            
            LANE DETECTION
            This section processes the frame for lane detection and returns the steering command.
            """
            if not DISABLE_LANE_DETECTION:
                steering_cmd, lane_debug = process_frame(small_frame.copy())
                combined_frame = lane_debug.copy()
            else:
                combined_frame = small_frame.copy()

            """
            OBJECT DETECTION
            This section detects objects in the frame and updates the state manager with the detected objects.
            """
            manbox_position = []
            crossbox_position = []
            detected_red = False
            detected_green = False

            if not DISABLE_OBJECT_DETECTION and frame_count % object_detection_interval == 0:
                detections = detect_objects(small_frame, size_scale)
                for label, conf, (x1, y1), (x2, y2) in detections:
                    logging.info(f"OBJECT: {label} | coords: ({x1},{y1}), ({x2},{y2})")
                    if DEBUG_MODE:
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
                    no_crossing_person_counter += 1
                else:
                    no_crossing_person_counter = 0

            # Display the frame with detected objects and lane markings
            if SHOW_VIDEO:
                cv2.imshow("Combined View", combined_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Update the state manager with the current information
            if DEBUG_MODE:
                logging.debug(f"Frame {frame_count}: Steering Command: {steering_cmd}, Manbox: {manbox_position}, Crossbox: {crossbox_position}, Detected Red: {detected_red}, Detected Green: {detected_green}")
            state_info = state_manager.update(
                steering_cmd, 
                manbox_position, 
                crossbox_position, 
                detected_red, 
                detected_green
            )

            lane_state_obj = state_info['lane_state'] # Gets the current lane state object e.g. Searching, Straight, Left, Right, SharpLeft, SharpRight
            override = state_info['override'] # True if crossing or traffic light state requires override

            if no_crossing_person_counter > no_crossing_person_threshold:
                state_manager.reset_crossing() # Reset crossing state if no person detected for a while

            if LOG_MODE:
                logging.info(f"Lane: {lane_state_obj.__class__.__name__}, Override: {override}")
                logging.info(f"Crossing State: {state_manager.cross_manager.state}")
                logging.info(f"Traffic Light State: {state_manager.traffic_manager.state}")
                logging.info(override)

            if override: # override happens due to crossing or traffic light
                if LOG_MODE:
                    logging.warning(f"Override triggered: {override}")

                controller.stop() # Stop the kart from moving
            else:
                lane_state_obj.act(controller) # Perform the action based on the current lane state

    finally:
        controller.steer(0.0) # Reset steering, because the kart breaks when stopped while wheels are turned
        cap.release()
        lidar_detector.stop()
        cv2.destroyAllWindows()
        bus.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run lane and object detection')
    parser.add_argument('source', help='Video file path or camera index')
    parser.add_argument('--camera', action='store_true', help='Use camera')
    args = parser.parse_args()
    main(args.source, is_camera=args.camera)
