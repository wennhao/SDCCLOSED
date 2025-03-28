import can

CAN_MESSAGE_SENDING_SPEED = 0.04

"""
Set the brake force for the kart.

:param bus: The CAN bus object.
:param force: The brake force (0-100).
:return: The task object for the periodic message.
"""
def set_brake_force(bus, force):
    
    # Ensure force is within valid range
    if not (0 <= force <= 100):
        raise ValueError("Force must be between 0 and 100.")
    
    brake_message = can.Message(
        arbitration_id=0x110,
        data=[0, 0, 0, 0, 0, 0, 0, 0],
        is_extended_id=False
    )
    brake_message.data = [force] + [0]*7
    brake_task.modify_data(brake_message)
    brake_task = bus.send_periodic(brake_message, CAN_MESSAGE_SENDING_SPEED)
    return brake_task