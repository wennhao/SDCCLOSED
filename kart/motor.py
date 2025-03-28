import can

CAN_MESSAGE_SENDING_SPEED = 0.04

"""
for byte 1 adjust to change the speed from 0 to 100
100 = max speed
for byte 3 adjust the following values for the following effects:
0 = neutral
1 = forward
2 = reverse 
"""

"""
Move the kart forward
This function sends a CAN message to move the kart forward.
:param bus: The CAN bus object.
:return: The task object for the periodic message.
"""
def move_forward(bus):
    motor_message = can.Message(
        arbitration_id=0x330,
        data=[100, 0, 1, 0, 0, 0, 0, 0],
        is_extended_id=False
    )
    motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED)
    return motor_task

"""
Stop the kart
This function sends a CAN message to stop the kart.
:param bus: The CAN bus object.
:return: The task object for the periodic message.
"""
def reset_motor(bus):
    motor_message = can.Message(
        arbitration_id=0x330,
        data=[0, 0, 0, 0, 0, 0, 0, 0],
        is_extended_id=False
    )
    motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED)
    return motor_task

"""
Move the kart backward
This function sends a CAN message to move the kart backward.
:param bus: The CAN bus object.
:return: The task object for the periodic message.
"""
def move_backward(bus):
    motor_message = can.Message(
        arbitration_id=0x330,
        data=[100, 0, 2, 0, 0, 0, 0, 0],
        is_extended_id=False
    )
    motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED)
    return motor_task