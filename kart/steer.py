import can
import struct

CAN_MESSAGE_SENDING_SPEED = 0.04

"""
This function is used to send a steering message to the right with no specific speed
PARAMETERS:
- The bus is the can bus object
- The angle is a float between -1.25 and 1.25
NOTE:
- 1.25 is the maximum angle to the right
- 0.0 is the center angle
- -1.25 is the maximum angle to the left
"""
def steer(bus, angle):
    if not (-1.25 <= angle <= 1.25):
        raise ValueError("Angle must be between -1.25 and 1.25")
    
    angle_bytes = struct.pack('<f', angle)  # < little-endian float f = float

    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [*angle_bytes, 0, 0, 0, 0],
        is_extended_id = False
    )

    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task


"""
This function is used to send a steering message to a certain angle with a specific speed
Speed should be given in bytes
PARAMETERS:
- The bus is the can bus object
- The angle is a float between -1.25 and 1.25
- The speed is a int between 0 and 100
NOTE:
- 1.25 is the maximum angle to the right
- 0.0 is the center angle
- -1.25 is the maximum angle to the left
- 0 is the minimum speed
- 100 is the maximum speed
- The speed is converted to a value between 0 and 255

"""
def steer_with_speed(bus, angle, speed):

    if not (-1.25 <= angle <= 1.25):
        raise ValueError("Angle must be between -1.25 and 1.25")
    
    angle_bytes = struct.pack('<f', angle)  # < little-endian float f = float

    if not (0 <= speed <= 100):
        raise ValueError("Speed must be between 0 and 100")
    
    speed_steps = int(speed * 50000 / 100)  # Convert speed to a value between 0 and 255

    # Convert speed to big-endian 4-byte integer
    speed_bytes = speed_steps.to_bytes(4, "big")  # 'big' = big-endian

    steer_message = can.Message(
        arbitration_id = 0x220,
          data=[*angle_bytes, *speed_bytes],
        is_extended_id = False
    )
    
    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task

