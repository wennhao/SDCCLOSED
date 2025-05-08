import cv2
import numpy as np
import time
import can
import struct

CAN_MESSAGE_SENDING_SPEED_MOTOR = 0.04
CAN_MESSAGE_SENDING_SPEED_STEER = 0.4

def initialize_can():
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus

def move_forward(speed):
    motor_message = can.Message(
        arbitration_id=0x330,
        data=[speed, 0, 1, 0, 0, 0, 0, 0],
        is_extended_id=False
    )
    # motor_message = [speed, 0, 1, 0, 0, 0, 0, 0]
    return motor_message

def steer(angle):
    if not (-1.25 < angle < 1.25):
        raise ValueError("Angle must be between -1.25 and 1.25")

    angle_bytes = struct.pack('<f', angle)  # < little-endian float f = float

    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [*angle_bytes, 0, 0, 0, 0],
        is_extended_id = False
    )
    # steer_message = [*angle_bytes, 0, 0, 0, 0]

    return steer_message

def main():
    bus = initialize_can()
    standard_speed = 100
    try:
        while:
            motor_message = move_forward(standard_speed)
            motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED_MOTOR)
            steer_message = steer(0.0)
            steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED_STEER)



            new_motor_message = move_forward(standard_speed)
            motor_task.modify_data(new_motor_message)

            #steer_task.modify_data(steer_angle)
            hardcode = steer(-0.65)
            steer_task.modify_data(hardcode)


    except KeyboardInterrupt:
        pass

    finally:
        if motor_task:
            motor_task.stop()
        if steer_task:    
            steer_task.stop()
        print("error / stopped")         

if __name__ == '__main__':
    main()

