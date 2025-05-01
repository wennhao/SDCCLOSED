#/usr/bin/env python3

import cv2
import numpy as np
import time
import can
import struct

CAN_MSG_SENDING_SPEED = .040 

def initialize_camera():
    capture = cv2.VideoCapture(2)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 848)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    capture.set(cv2.CAP_PROP_FOCUS, 0)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) #important to set right codec to enable 60fps
    capture.set(cv2.CAP_PROP_FPS, 30) #make 60 to enable 60FPS
    return capture

def initialize_can():
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus


def main():
    bus = initialize_can()

    front_camera = initialize_camera()

    try:
        while (True):
            _, frame = front_camera.read()
            
            cv2.imshow('Camera preview', frame)
            cv2.waitKey(1)
        
    except KeyboardInterrupt:
        pass
    
    front_camera.release()
    cv2.destroyAllWindows()        

if __name__ == '__main__':
    main()