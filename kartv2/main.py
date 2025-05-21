#!/usr/bin/env python3
import argparse
import logging
import sys
import cv2
import can

from motor import forward_message
from steer import steer_message
from brake import set_brake_force_message

from controllers.fsm import KartFSM, TrafficLightState
from controllers.detector_manager import MasterStateManager, LaneState  # detection logic
from linedetection.linedetection import process_frame
from objectdetection.objecttest import detect_objects

# Configure logging
default_format = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=default_format)

# Constants
ANGLE_LEFT = -0.65
ANGLE_LEFT_SHARP = -1.20
ANGLE_CENTER = 0.0
ANGLE_RIGHT = 0.65
ANGLE_RIGHT_SHARP = 1.20

# CAN initialization
DEBUG_MODE = True  # set True to disable real CAN sends
def initialize_can():
    if DEBUG_MODE:
        return can.Bus(interface='virtual', channel='vcan0', bitrate=500000,
                       receive_own_messages=True)
    else:
        return can.Bus(interface='socketcan', channel='can0', bitrate=500000)


def main(source: str, is_camera: bool):
    # Initialize CAN bus
    bus = initialize_can()

    # Wrap CAN senders for FSM
    fsm = KartFSM(
        steer_fn=lambda ang: bus.send(steer_message(ang)),
        forward_fn=lambda sp: bus.send(forward_message(sp)),
        brake_fn=lambda bf: bus.send(set_brake_force_message(bf))
    )

    # Detection manager for traffic/ped logic
    det_manager = MasterStateManager()

    # Video capture
    cap = cv2.VideoCapture(int(source) if is_camera else source)
    if not cap.isOpened():
        logging.error(f"Unable to open {'camera' if is_camera else 'video'}: {source}")
        sys.exit(1)

    frame_count = 0
    frame_skip = 10
    object_interval = 5
    size_scale = 0.2

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip:
                continue

            # Resize
            small = cv2.resize(frame, (0,0), fx=size_scale, fy=size_scale)

            # Lane detection
            steering_cmd, lane_vis = process_frame(small)
            vis = lane_vis.copy() if lane_vis is not None else small.copy()

            # Object detection
            detections = []
            if frame_count % object_interval == 0:
                detections = detect_objects(small, size_scale)
                # draw boxes
                for label, conf, (x1,y1), (x2,y2) in detections:
                    cv2.rectangle(vis, (x1,y1), (x2,y2), (0,150,0), 2)
                    cv2.putText(vis, f"{label} {conf:.2f}", (x1, y1-5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,150,0), 2)

            # Update detection-based states
            state_info = det_manager.update_states(steering_cmd or '', detections)
            traffic_state = state_info['traffic_state']
            override_flag = state_info['override']

            # Compute FSM inputs
            lane_found = det_manager.lane_state.state != LaneState.SEARCHING
            ped_on_cross = override_flag and traffic_state != TrafficLightState.RED
            light_st = traffic_state if traffic_state in TrafficLightState else TrafficLightState.NONE

            # Drive FSM
            current_state = fsm.update(lane_found, light_st, ped_on_cross)
            logging.info(f"FSM State: {current_state}")

            # Display
            cv2.imshow('Debug', vis)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        bus.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run kart main loop')
    parser.add_argument('source', help='Video path or camera index')
    parser.add_argument('--camera', action='store_true', help='Use camera input')
    args = parser.parse_args()
    main(args.source, args.camera)
