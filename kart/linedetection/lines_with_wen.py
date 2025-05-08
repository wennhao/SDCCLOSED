#/usr/bin/env python3

import cv2
import numpy as np
import time
import can
import struct

CAN_MESSAGE_SENDING_SPEED = 0.04

def initialize_camera():
    capture = cv2.VideoCapture(0)
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
    x_norm = 540

    roi_border = width // 8 * 3

    region_vertices = [(roi_border, 0), (width, 0), (width, height), (roi_border, height)]
    roi = region_of_interest(edges, np.array([region_vertices], np.int32))
    lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)
    
    x_at_target_values = []

    if lines is not None:
        for line in lines:
            x_val = get_x(line[0], y_norm)
            if x_val is not None:
                x_at_target_values.append(x_val)

    if x_at_target_values:
        x_at_target = int(np.median(x_at_target_values))
        if x_at_target < x_norm - 25: # example values
            print("left")
            return (-0.4) # left
        elif x_at_target > x_norm + 25: # example values, maybe make them linear / exponential
            print("right")
            return 0.4 # right
        else:
            print("straight")
            return 0


def move_forward(speed):
    # motor_message = can.Message(
    #     arbitration_id=0x330,
    #     data=[speed, 0, 1, 0, 0, 0, 0, 0],
    #     is_extended_id=False
    # )
    motor_message = [speed, 0, 1, 0, 0, 0, 0, 0]
    return motor_message

def steer(angle):
    if not (-1.25 < angle < 1.25):
        raise ValueError("Angle must be between -1.25 and 1.25")

    angle_bytes = struct.pack('<f', angle)  # < little-endian float f = float

    # steer_message = can.Message(
    #     arbitration_id = 0x220,
    #     data = [*angle_bytes, 0, 0, 0, 0],
    #     is_extended_id = False
    # )
    steer_message = [*angle_bytes, 0, 0, 0, 0]

    return steer_message


def main():
    bus = initialize_can()

    front_camera = initialize_camera()

    start_time = time.time()
    time_diff = 0

    motor_task = None
    steer_task = None
    
    try:
        motor_message = move_forward(25)
        motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED)
        steer_message = steer(0)
        steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)

        try:
            while (time_diff < 30):

                ret, frame = front_camera.read()
                
                if not ret:
                    print("failed to read frame")

                steering = detect_lanes(frame)
                steer_angle = steer(steering)
                steer_message.modify_data(steer_angle)

                end_time = time.time()
                time_diff = end_time - start_time

                time.sleep(0.33)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exit key pressed.")
                    break

        except KeyboardInterrupt:
            pass

        motor_task.stop()
        steer_task.stop()

    finally:
        motor_task.stop()
        steer_task.stop()

    front_camera.release()
    cv2.destroyAllWindows()        

if __name__ == '__main__':
    main()
    
"""
Steer task aanmaken, elke iteratie vd loop de inhoud van die task aanpassen
of
Elke iteratie vd loop en task stoppen en een nieuwe aanmaken

??
hoef niet eens een message die herhaalt stuurt te maken
kan gwn voor iedere iteratie 1 message sturen
??
"""