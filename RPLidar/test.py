#!/usr/bin/env python3

import argparse
from os import path
from platform import system

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import use
from rplidar import RPLidar

BAUDRATE: int = 115200
TIMEOUT: int = 1
DMAX: int = 4000
IMIN: int = 0
IMAX: int = 50

# Set the threshold to 50 cm (which is 500 mm)
FRONT_THRESHOLD_MM = 500

def update_line(num, iterator, line):
    scan = next(iterator)
    # Update scatter plot with angle (in radians) and distance values.
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    line.set_offsets(offsets)
    intents = np.array([meas[0] for meas in scan])
    line.set_array(intents)
    
    # Initialize detection flags.
    detected_front = False
    detected_left = False
    detected_right = False

    # Process each measurement in the scan.
    for intensity, angle, distance in scan:
        # Define "front" as measurements with angle <= 15° or >= 345°.
        if angle <= 15 or angle >= 345:
            if distance < FRONT_THRESHOLD_MM:
                detected_front = True
        # Define "front left" as measurements with angle between 15° and 90°.
        elif 15 < angle < 90:
            detected_left = True
        # Define "front right" as measurements with angle between 270° and 345°.
        elif 270 < angle < 345:
            detected_right = True

    # Print detection messages if conditions are met.


    if detected_front:
        print(f"Warning: Object detected in front within 5 cm!")
    else :
        print("No object detected")
    # if detected_left:
    #     print("Object detected on the front left!")
    # if detected_right:
    #     print("Object detected on the front right!")
    
    return line

def run():
    if system() == 'Darwin':
        use('MacOSX')

    description = 'RPLIDAR device plot with simple object detection'
    epilog = 'The author assumes no liability for any damage caused by use.'
    parser = argparse.ArgumentParser(prog='./device_plot.py', description=description, epilog=epilog)
    parser.add_argument('device', help="device path", type=str)
    args = parser.parse_args()
    dev_path = args.device

    if path.exists(dev_path):
        print('Found device: {0}'.format(dev_path))
        print('To stop - close the plot window')

        lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)

        fig = plt.figure()
        title = 'RPLIDAR'
        fig.set_label(title)
        fig.canvas.manager.set_window_title(title)

        ax = plt.subplot(111, projection='polar')
        line = ax.scatter([0, 0], [0, 0], s=5, c=[IMIN, IMAX], cmap=plt.cm.Greys_r, lw=0)
        ax.set_title('360° scan result')
        ax.set_rmax(DMAX)
        ax.grid(True)

        iterator = lidar.iter_scans()
        ani = animation.FuncAnimation(fig, update_line, fargs=(iterator, line), interval=50)

        plt.show()
        lidar.stop()
        lidar.disconnect()
    else:
        print('[Error] Could not find device: {0}'.format(dev_path))


          

def main():
    run()


if __name__ == '__main__':
    main()
