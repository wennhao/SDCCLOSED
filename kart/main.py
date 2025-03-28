import can
from time import sleep
import struct
import steer, brake, motor

# change the interface to virtual for testing
# change the interface to socketcan for real testing
def initialize_can():
    bus = can.Bus(interface='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    return bus

def send_test_message(bus):
    message = can.Message(arbitration_id=0x220, data=[1, 2, 3, 4, 5, 6, 7, 8], is_extended_id=False)
    bus.send(message)
    print("Sent test message!")

def convert_to_ieee754(value):
    res = list(bytearray(struct.pack("f", value))) + [0]*4
    print(res)
    return res


def main():
    bus = initialize_can() # call function to intialize the can
    # steer.steer_left(bus) # call function to steer left but send bus
    # sleep(1) # wait for 1 second
    # steer.steer_right(bus) # call function to steer right but send bus
    # convert_to_ieee754(-1.0) # call function to convert to ieee754
    bus.shutdown() # shutdown the bus

# runs main
if __name__ == "__main__":
    main()