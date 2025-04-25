from time import sleep
import can


CAN_MESSAGE_SENDING_SPEED = 0.04


def initialize_can(): #Set up the can bus interface
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus
    
    
def main():
    bus = initialize_can()
    
    brake_message = can.Message(arbitration_id=0x110, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
    # data[0] kan van 0 tm 100. dit geeft het percentage van de maximum rem kracht dat gegenereerd kan worden
    brake_task = bus.send_periodic(brake_message, CAN_MESSAGE_SENDING_SPEED)
    
    brake_message.data = [50] + [0]*7 # 50% remkracht
    brake_task.modify_data(brake_message)

    sleep(2)

    brake_message.data = [0]*8 # 0% remkracht
    brake_task.modify_data(brake_message)

    sleep(2)


if __name__ == '__main__':
    main()