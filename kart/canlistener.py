import can

bus = can.Bus(interface="virtual", channel="vcan", bitrate=500000, receive_own_messages=True)

print("Listening for CAN messages...")

while True:
    msg = bus.recv()  # Wait for a message
    print(f"Received: {msg}")
