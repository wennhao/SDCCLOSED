import can
from time import sleep
import struct
import steer as kart, brake as kart, motor as kart
# or i can do this
# import steer as SteerManager, brake as BrakeManager, motor as MotorManager

angle_left = -1.25
angle_center = 0.0
angle_right = 1.25
max_speed = 100
min_speed = 0

# change the interface to virtual for testing
# change the interface to socketcan for real testing
def initialize_can():
    bus = can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    return bus

def send_test_message(bus):
    message = can.Message(arbitration_id=0x220, data=[1, 2, 3, 4, 5, 6, 7, 8], is_extended_id=False)
    bus.send(message)
    print("Sent test message!")

# This function is used to convert a float to a list of bytes in IEEE 754 format
def convert_to_ieee754(value):
    res = list(bytearray(struct.pack("f", value))) + [0]*4
    print(res)
    return res


def main():
    bus = initialize_can() # call function to intialize the can
    kart.steer(bus, angle_left) # call function to steer left
    sleep(1) # wait for 1 second
    kart.steer(bus, angle_right) # call function to steer right
    # convert_to_ieee754(-1.0) # call function to convert to ieee754
    kart.steer_with_speed(bus, angle_left, max_speed) # call function to steer left with increased speed
    bus.shutdown() # shutdown the bus

# runs main
if __name__ == "__main__":
    main()