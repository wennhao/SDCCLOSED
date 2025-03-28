import can

CAN_MESSAGE_SENDING_SPEED = 0.04

"""
This function is used to send a steering message to the right with no specific speed
"""
def steer_right(bus):
    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [0, 0, 128, 62, 0, 0, 0, 0],
        is_extended_id = False)
    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task


"""
This function is used to send a sterring message to the right with a specific speed
Speed should be given in bytes
TODO:
- Add a check to see if the speed is in the range of 0-100
- Add custom speed parameter to function with speed
"""
def steer_right_with_speed(bus, speed):
    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [0, 0, 0, 128, 62, 0, 0, 0],
        is_extended_id = False)
    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task

"""
This function is used to send a steering message to the left with no specific speed"
"""
def steer_left(bus):
    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [0, 0, 128, 191, 0, 0, 0, 0],
        is_extended_id = False)
    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task
"""
This function is used to send a steering message to the left with a specific speed
Speed should be given in bytes
TODO:
- Add a check to see if the speed is in the range of 0-100
- Add custom speed parameter to function with speed
"""
def steer_left_with_speed(bus, speed):
    steer_message = can.Message(
        arbitration_id = 0x220,
        data = [0, 0, 0, 128, 191, 0, 0, 0],
        is_extended_id = False)
    steer_task = bus.send_periodic(steer_message, CAN_MESSAGE_SENDING_SPEED)
    return steer_task