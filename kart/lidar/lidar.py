import sys
from os import path
from platform import system
import numpy as np
from rplidar import RPLidar

# --- CONFIG ---
LIDAR_PORT = '/dev/cu.usbserial-0001'
BAUDRATE = 256000
TIMEOUT = 1
DMAX = 4000  # max distance for potential future use
IMIN = 0     # min intensity for potential future use
IMAX = 50    # max intensity for potential future use

FRONT_THRESH = 500
RIGHT_THRESH = 500 # 50 cm
LEFT_THRESH = 500


def detect_objects(scan):

    detected_front = False
    detected_left = False
    detected_right = False

    for _, angle, distance in scan:
        # Front: angle <= 15° or >= 345°
        if angle <= 15 or angle >= 345:
            if distance < FRONT_THRESH:
                detected_front = True
        # Front-left: 15° < angle < 90°
        elif 15 < angle < 90:
            if distance < LEFT_THRESH:
                detected_left = True
        # Front-right: 270° < angle < 345°
        elif 270 < angle < 345:
            if distance < RIGHT_THRESH:
                detected_right = True

    return detected_front, detected_left, detected_right


def run():

    device_path = LIDAR_PORT
    if not path.exists(device_path):
        print(f"[Error] Could not find device: {device_path}")
        sys.exit(1)

    print(f"Found device: {device_path}")
    print("Press Ctrl+C to stop.")

    lidar = RPLidar(port=device_path, baudrate=BAUDRATE, timeout=TIMEOUT)

    try:
        for scan in lidar.iter_scans():
            front, left, right = detect_objects(scan)

            if front:
                print("Warning: Object detected in front within 50 cm!")
            # if left:
            #     print("Warning: Object detected on the left within 50 cm!")
            # if right:
            #     print("Warning: Object detected on the right within 50 cm!")
            else:
                print("No object detected within 50 cm.")

    except KeyboardInterrupt:
        print("\nStopping LIDAR and exiting.")
    finally:
        lidar.stop()
        lidar.disconnect()


if __name__ == '__main__':
    run()
