import argparse
import logging
import cv2
import can

from time import sleep
from linedetection.linedetection import process_frame # Function
from objectdetection.objectdetection import detect_objects # Function
from carcontroller import CarController # Class
from statemachine.master_state_manager import MasterStateManager # Class
from initcameras.initializecameras import initialize_cameras

# Lidar
from lidar.lidar_detection import LidarDetector # Class

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Constants
DEBUG_MODE = False
SHOW_VIDEO = False
DISABLE_OBJECT_DETECTION = False
DISABLE_LANE_DETECTION = False
DISABLE_LIDAR = True # Lidar does not work, disabled by default
LOG_MODE = True
LINUX_MODE = True

lidar_port = '/dev/ttyUSB0' if LINUX_MODE else 'com6' # Adjust port based on OS
# Variables
size_scale = 0.6 if DEBUG_MODE else 1.0
frame_skip = 10
object_detection_interval = 5
lane_detection_interval = 2

no_crossing_person_threshold = 100
frames_after_left_turn_threshold = 200
ready_to_cross_counter_threshold = 500
stop_sign_wait_for = 200
stop_sign_ignore_for = 500

lidar_front_crash_prevention_distance = 500

straight_on_crossing_for = 400

def initialize_can():
    if DEBUG_MODE:
        return can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    else:
        return can.Bus(interface='socketcan', channel='can0', bitrate=500000)

def main(source: str, is_camera: bool = False):
    bus = initialize_can()
    controller = CarController(bus, debug=DEBUG_MODE)
    state_manager = MasterStateManager()


    if DEBUG_MODE:
        cap = cv2.VideoCapture(int(source) if is_camera else source)
        if not cap.isOpened():
            print(f"Error: Could not open {'camera' if is_camera else 'video file'}: {source}")
            return
    else:
        cameras = initialize_cameras()
        front_camera = cameras["front"]
        left_camera = cameras["left"]
        right_camera = cameras["right"]

    # Lidar setup
    if not DISABLE_LIDAR:
        lidar_detector = LidarDetector(port=lidar_port, baudrate=115200, timeout=1, debug=DEBUG_MODE)
        lidar_detector.start()  # Start the Lidar thread

    frame_count = 0
    no_crossing_person_counter = 0

    left_turn_state = False
    frames_after_left_turn = 0

    ready_to_cross_counter = 0

    stop_sign_state = False
    stop_sign_counter = 0
    stop_sign_ignore_state = False
    stop_sign_ignore_counter = 0
    
    override = False

    crossing_found_state = False
    crossing_found_counter = 0

    try:
        while True:
            """
            FRAME PROCESSING
            Video Capture setup and frame reading.
            """
            if DEBUG_MODE:
                ret, frame = cap.read()
                if not ret:
                    break
                left_camera_frame = frame.copy()
                right_camera_frame = frame.copy()
            else:
                retl, left_camera_frame = left_camera.read()
                retf, frame = front_camera.read()
                retr, right_camera_frame = right_camera.read()
            
                if not retl or not retf or not retr:
                    logging.error("Failed to read from one or more cameras")
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
                front_dist, left_dist, right_dist = lidar_detector.get_obstacles()
                print(f"LIDAR: {front_dist}, {left_dist}, {right_dist}")

                if front_dist < lidar_front_crash_prevention_distance:
                    logging.warning("LIDAR: Obstacle detected in front!")
                    override = True
            else: 
                front_dist = 0
                left_dist = 0
                right_dist = 0
            """
            
            LANE DETECTION
            This section processes the frame for lane detection and returns the steering command.
            """
            
            if not DISABLE_LANE_DETECTION and frame_count % lane_detection_interval == 0:
                if left_turn_state:
                    steering_cmd, lane_debug = process_frame(left_camera_frame, "LEFT")
                else:
                    steering_cmd, lane_debug = process_frame(right_camera_frame, "RIGHT")


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
            left_turn_sign = False
            detected_car = False

            if not DISABLE_OBJECT_DETECTION and frame_count % object_detection_interval == 0:
                detections = detect_objects(small_frame, size_scale)
                for label, conf, (x1, y1), (x2, y2) in detections:
                    logging.info(f"OBJECT: {label} | coords: ({x1},{y1}), ({x2},{y2})")
                    if DEBUG_MODE:
                        cv2.rectangle(combined_frame, (x1, y1), (x2, y2), (0, 50, 150), 2)
                        cv2.putText(combined_frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 150), 2)

                    if label == 'zebra-crossing':
                        crossbox_position = [x1, y1, x2, y2]
                        crossing_found_state = True
                    elif label == 'person':
                        manbox_position = [x1, y1, x2, y2]
                    elif label == 'traffic-light-red':
                        detected_red = True
                    elif label == 'traffic-light-green':
                        detected_red = False
                        detected_green = True
                    elif label == 'one-way-left' or label == 'sign-left-only':
                        left_turn_sign = True
                        left_turn_state = True
                    elif label == 'stop-sign':
                        stop_sign_state = True
                    elif label == 'car':
                        detected_car = True

                # If one of the left turn signs is detected, set state for as long as the sign is detected + threshold frames
                # State is used to switch camera sides
                if not left_turn_sign:
                    frames_after_left_turn += 1
                    if frames_after_left_turn > frames_after_left_turn_threshold:
                        left_turn_state = False
                else:
                    frames_after_left_turn = 0

                # If there's no person that needs to cross, increase the counter every frame
                # If the counter reaches the threshold, reset the crossing state
                if not manbox_position or not crossbox_position or state_manager.crossed():
                    no_crossing_person_counter += 1
                    if no_crossing_person_counter > no_crossing_person_threshold:
                        state_manager.reset_crossing() # Reset crossing state if no person detected for a while
                else:
                    no_crossing_person_counter = 0

                # If kart is waiting on pedestrian to cross, increase counter every frame
                # If counter reaches threshold, set state to crossed
                # Next frame the above if statement would be True
                if state_manager.waiting():
                    ready_to_cross_counter += 1
                    if ready_to_cross_counter > ready_to_cross_counter_threshold:
                        state_manager.alreadycrossed() # If the person for some reason is just waiting near the crosswalk. It will ignore for <no_crossing_person_threshold> frames
                else:
                    ready_to_cross_counter = 0

                # If stop sign is detected, increase counter every frame
                # During stop sign, kart is stopped
                # If counter reaches threshold, reset stop sign state and set ignore state (see next if-statement)
                # With state reset, kart can drive again
                if stop_sign_state:
                    stop_sign_counter += 1
                    if stop_sign_counter > stop_sign_wait_for and not stop_sign_ignore_state: # Keeps counting, so delay is just ignore_for
                        stop_sign_state = False
                        stop_sign_ignore_state = True
                else:
                    stop_sign_counter = 0

                # If stop sign ignore state, increase counter every frame
                # Ignore state ignores stop sign functionality so it doesn't stay stopped forever
                # If counter reaches threshold, reset state
                if stop_sign_ignore_state:
                    stop_sign_ignore_counter += 1
                    if stop_sign_ignore_counter > stop_sign_ignore_for:
                        stop_sign_ignore_state = False
                else:
                    stop_sign_ignore_counter = 0

                straight_on_crossing_state = crossing_found_state and not state_manager.get_cross_state()
                if straight_on_crossing_state:
                    crossing_found_counter += 1
                    if crossing_found_counter > straight_on_crossing_for:
                        crossing_found_state = False
                        straight_on_crossing_state = False
                else:
                    crossing_found_counter = 0

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
                detected_green,
                stop_sign_state,
                detected_car,
                front_dist, left_dist, right_dist,
                straight_on_crossing_state
            )

            lane_state_obj = state_info['lane_state'] # Gets the current lane state object e.g. Searching, Straight, Left, Right, SharpLeft, SharpRight
            override = override or state_info['override'] # True if crossing or traffic light state requires override or crash prevention

            if LOG_MODE:
                logging.info(f"Lane: {lane_state_obj.__class__.__name__}, Override: {override}")
                logging.info(f"Crossing State: {state_manager.cross_manager.state}")
                logging.info(f"Traffic Light State: {state_manager.traffic_manager.state}")
                logging.info(f"Left Turn State: {left_turn_state}")
                logging.info(f"COM: {state_info['com_state']}")
                logging.info(override)

            if override: # override happens due to crossing or traffic light
                if LOG_MODE:
                    logging.warning(f"Override triggered: {override}")

                controller.stop() # Stop the kart from moving
            else:
                lane_state_obj.act(controller) # Perform the action based on the current lane state

    finally:
        controller.steer(0.0) # Reset steering, because the kart breaks when stopped while wheels are turned

        if DEBUG_MODE:
            cap.release()
        else:
            front_camera.release()
            left_camera.release()
            right_camera.release()
        lidar_detector.stop()
        cv2.destroyAllWindows()
        bus.shutdown()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run lane and object detection')
    parser.add_argument('source', help='Video file path or "true" to use camera')
    #parser.add_argument('--camera', action='store_true', help='Use camera')
    args = parser.parse_args()
    
    use_cameras = False
    if args.source.lower() == "true": # Put python main.py true to use camera's instead of video file
        use_cameras = True
        source = 0
    else: 
        source = args.source
    main(source, is_camera=use_cameras)