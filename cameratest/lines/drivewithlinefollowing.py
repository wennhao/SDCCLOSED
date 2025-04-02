# inspiratie van drive_with_neural_network.py van SDC GitHub:

#/usr/bin/env python3

import cv2
import numpy as np
import can
import struct

CAN_MSG_SENDING_SPEED = .040

def initialize_cameras() -> Dict[str, cv2.VideoCapture]:
    """
    Initialize the opencv camera capture devices.
    """
    config: video.CamConfig = video.get_camera_config()
    if not config:
        print('No valid video configuration found!', file=sys.stderr)
        exit(1)
    cameras: Dict[str, cv2.VideoCapture] = dict()
    for camera_type, path in config.items():
        capture = cv2.VideoCapture(path)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 848)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        capture.set(cv2.CAP_PROP_FOCUS, 0)
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) #important to set right codec to enable 60fps
        capture.set(cv2.CAP_PROP_FPS, 30) #make 60 to enable 60FPS
        cameras[camera_type] = capture
    return cameras


def initialize_can():
    """
    Set up the can bus interface
    """
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus


def main():
    bus = initialize_can()

    cameras = initialize_cameras()
    front_camera = cameras["front"]

    try:
        # Define messages
        brake_msg = can.Message(arbitration_id=0x110, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        brake_task = bus.send_periodic(brake_msg, CAN_MSG_SENDING_SPEED)
        steering_msg = can.Message(arbitration_id=0x220, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        steering_task = bus.send_periodic(steering_msg, CAN_MSG_SENDING_SPEED)
        throttle_msg = can.Message(arbitration_id=0x330, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        throttle_task = bus.send_periodic(throttle_msg, CAN_MSG_SENDING_SPEED)

        # brake_msg.data = [int(99*max(0, 1))] + 7*[0]
        # beginnen met rijden
        throttle_msg.data = [int(99*max(0, 1)), 0, 1] + 5*[0]
        
        # brake_msg.modify_data(brake_msg)
        throttle_task.modify_data(throttle_msg)

        try:
            while (True):
                _, frame = front_camera.read()

                cv2.imshow('Camera preview', frame)
                cv2.waitKey(33) #33.3334 ms wachten voor 30 FPS

                frame = np.resize(frame[:,:,::-1]/255, (1, 144, 256, 3)).astype(np.float32)

                steering_angle = detect_lanes(frame)

                steering_msg.data = list(bytearray(struct.pack("f", float(steering_angle)))) + [0]*4

                steering_task.modify_data(steering_msg)

        except KeyboardInterrupt:
            pass

    finally:
        throttle_task.stop()
        steering_task.stop()
        brake_task.stop()


y_target = 500
x_target = 0 # standaard positie van de lijn bij y=500 (nog niet goed ingesteld)


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def get_x(lines):
    for x1, y1, x2, y2 in lines:
        m = (x2 - x1) / (y2 - y1)
        x_coord = x1 + (y_target - y1) * m
        return int(x_coord)
    return None


def detect_lanes(frame):
    if not frame:
        print("Error: No frame.")
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    height, width = edges.shape
    region_vertices = [(0, height // 2), (width, height // 2), (width, height), (0, height)]
    roi = region_of_interest(edges, np.array([region_vertices], np.int32))

    lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)

    x_at_target_values = []

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 != x2 and y1 != y2:
                    x_at_target_values.append(get_x(line)) 
                    # alleen doen als het bepaalde afstand heeft van x_target ?

    if x_at_target_values:
        x_at_target = np.mean(x_at_target_values)
        if x_at_target > x_target - 50 & x_at_target < x_target + 50:
            print("steer forward")
            return 0
        elif x_at_target < x_target - 50: # voorbeeld waardes
            print("steer left")
            return -0.5
        elif x_at_target > x_target + 50: # voorbeeld waardes
            print("steer right")
            return 0.5
        # hoe verder x_at_target van x_target vandaan is, hoe meer er wordt gestuurd ?
        # bij het insturen ook iets vertragen?


if __name__ == '__main__':
    main()