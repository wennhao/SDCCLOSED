#/usr/bin/env python3

import cv2
import numpy as np
import time
import can
import struct

CAN_MSG_SENDING_SPEED = .040

"""
def initialize_cameras() -> Dict[str, cv2.VideoCapture]:

    #Initialize the opencv camera capture devices.

    config: video.CamConfig = video.get_camera_config()
    if not config:
        print('No valid video configuration found!')
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
"""    

def initialize_can():
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus

def main():
    bus = initialize_can()

    # cameras = initialize_cameras()
    # front_camera = cameras["front"]
    front_camera = cv2.VideoCapture(2)

    try:
        brake_msg = can.Message(arbitration_id=0x110, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        brake_task = bus.send_periodic(brake_msg, CAN_MSG_SENDING_SPEED)
        steering_msg = can.Message(arbitration_id=0x220, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        steering_task = bus.send_periodic(steering_msg, CAN_MSG_SENDING_SPEED)
        throttle_msg = can.Message(arbitration_id=0x330, is_extended_id=False, data=[0, 0, 0, 0, 0, 0, 0, 0])
        throttle_task = bus.send_periodic(throttle_msg, CAN_MSG_SENDING_SPEED)

        try:
            while (True):
                _, frame = front_camera.read()
                
                cv2.imshow('Camera preview', frame)
                cv2.waitKey(1)
                
                #frame = np.resize(frame[:,:,::-1]/255, (1, 144, 256, 3)).astype(np.float32)
                
                steering = detect_lanes(frame)
                
                steering_msg.data = list(bytearray(struct.pack("f", float(steering)))) + [0]*4
                throttle_msg.data = [int(99*max(0, 10)), 0, 1] + 5*[0]
                
                brake_msg.modify_data(brake_msg)
                steering_task.modify_data(steering_msg)
                throttle_task.modify_data(throttle_msg)
        
        except KeyboardInterrupt:
            pass

    finally:
        throttle_task.stop()
        steering_task.stop()
        brake_task.stop()
        
        front_camera.release()
        cv2.destroyAllWindows()


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_x(line, y_norm):
    x1, y1, x2, y2 = line
    if x1 == x2:  # vertical line
        return x1
    if (y1 - y_norm) * (y2 - y_norm) > 0: # line does not cross y_norm
        return None

    m = (y2 - y1) / (x2 - x1)
    if m == 0:
        return None
    x = x1 + (y_norm - y1) / m
    return int(x)

def detect_lanes(frame):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.inRange(gray, 150, 255) # 200 - 255 voor rechter camera

    edges = cv2.Canny(grayscale, 70, 200)

    height, width = edges.shape
    y_norm = int(height / 2)
    x_norm = 550

    roi_border = width // 8 * 3

    region_vertices = [(roi_border, 0), (width, 0), (width, height), (roi_border, height)] # rechterkant
    roi = region_of_interest(edges, np.array([region_vertices], np.int32))
    lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)

    x_at_target_values = []

    x_at_target_values = []

    if lines is not None:
        for line in lines:
            x_val = get_x(line[0], y_norm)
            if x_val is not None:
                x_at_target_values.append(x_val)

    if x_at_target_values:
        x_at_target = int(np.median(x_at_target_values))
        if x_at_target < x_norm - 25: # example values
            return -1 # left
        elif x_at_target > x_norm + 25: # example values, maybe make them linear / exponential
            return 1 # right
        else:
            return 0

if __name__ == '__main__':
    main()