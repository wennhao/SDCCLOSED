#!/usr/bin/env python3
import time
from rplidar import RPLidar
import can

# --- CONFIG ---
LIDAR_PORT       = '/dev/ttyUSB0'      # or 'COM4' on Windows
BAUDRATE         = 115200
FRONT_THRESH     = 500                 # mm
SIDE_THRESH      = 500                 # mm (you can use a different threshold)
CAN_CHANNEL      = 'can0'
CAN_BITRATE      = 500000
CAN_PERIOD       = 0.05                # 20 Hz
# ---------------

# --- SETUP CAN ---
bus = can.Bus(interface='socketcan', channel=CAN_CHANNEL, bitrate=CAN_BITRATE)
brake_msg  = can.Message(arbitration_id=0x110, is_extended_id=False, data=[0]*8)
brake_task = bus.send_periodic(brake_msg, CAN_PERIOD)

def send_brake(level: float):
    brake_msg.data[0] = int(max(0, min(1, level)) * 99)
    brake_task.modify_data(brake_msg)

# --- MAIN LIDAR LOOP ---
lidar = RPLidar(port=LIDAR_PORT, baudrate=BAUDRATE)
print("Starting LiDAR + brake loop… Ctrl-C to exit.")

try:
    for scan in lidar.iter_scans():
        # --- slice out each sector ---
        front  = [dist for _, angle, dist in scan
                  if angle <= 15 or angle >= 345]
        left   = [dist for _, angle, dist in scan
                  if 15 < angle < 90]
        right  = [dist for _, angle, dist in scan
                  if 270 < angle < 345]

        # --- compute minima (or inf if empty) ---
        min_f = min(front ) if front  else float('inf')
        min_l = min(left  ) if left   else float('inf')
        min_r = min(right ) if right  else float('inf')

        # --- decide actions ---
        if min_f < FRONT_THRESH:
            print(f"[FRONT] Obstacle at {min_f:.0f} mm → FULL BRAKE")
            send_brake(1.0)
        else:
            send_brake(0.0)

        if min_l < SIDE_THRESH:
            print(f"[LEFT ] Obstacle at {min_l:.0f} mm")
        if min_r < SIDE_THRESH:
            print(f"[RIGHT] Obstacle at {min_r:.0f} mm")

        # throttle loop timing
        time.sleep(CAN_PERIOD)

except KeyboardInterrupt:
    print("Stopping…")
finally:
    lidar.stop()
    lidar.disconnect()
    brake_task.stop()
    bus.shutdown()
