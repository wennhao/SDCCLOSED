import can
from time import sleep
import struct
import converter
# import steer as kart, brake as kart, motor as kart # this does not work
# or i can do this
import steer as SteerManager, brake as BrakeManager, motor as MotorManager

# Variables
angle_left = -1.25
angle_center = 0.0
angle_right = 1.25
max_speed = 100
min_speed = 0

# change the interface to virtual for testing
# change the interface to socketcan and can0 for real testing
def initialize_can():
    bus = can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    return bus

def send_test_message(bus):
    message = can.Message(arbitration_id=0x220, data=[1, 2, 3, 4, 5, 6, 7, 8], is_extended_id=False)
    bus.send(message)
    print("Sent test message!")



def main():
    # bus = initialize_can() # call function to intialize the can
    bus = initialize_can() # call function to intialize the can
    bus.shutdown() # shutdown the bus

    # convert_to_ieee754(-1.0) # call function to convert to ieee754

# runs main
if __name__ == "__main__":
    main()