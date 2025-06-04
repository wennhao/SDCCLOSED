import threading
from os import path
from rplidar import RPLidar, RPLidarException
import sys
import time

class LidarDetector(threading.Thread):
    def __init__(self, port='com4', baudrate=115200, timeout=1, front_thresh=500, left_thresh=500, right_thresh=500, debug=False):
        super().__init__()
        self.daemon = True
        self.running = False

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.front_thresh = front_thresh
        self.left_thresh = left_thresh
        self.right_thresh = right_thresh

        self.front = False
        self.left = False
        self.right = False
        self.debug = debug

        self.lidar = None

    def _connect_lidar(self):
        if not path.exists(self.port):
            print(f"[Error] Could not find device: {self.port}")
            sys.exit(1)

        try:
            self.lidar = RPLidar(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            if self.debug:
                print("[LIDAR] Connected successfully.")
        except Exception as e:
            print(f"[LIDAR Error] Failed to connect: {e}")
            sys.exit(1)

    def run(self):
        self.running = True
        self._connect_lidar()
        last_heartbeat = time.time()

        while self.running:
            try:
                for scan in self.lidar.iter_scans():
                    if not self.running:
                        break

                    self.process_scan(scan)

                    # Heartbeat debug
                    if self.debug and time.time() - last_heartbeat > 5:
                        print(f"[LIDAR] Running... Front: {self.front}, Left: {self.left}, Right: {self.right}")
                        last_heartbeat = time.time()

            except RPLidarException as e:
                print(f"[LIDAR Error]: {e}")
                print("[LIDAR] Attempting to reconnect in 2 seconds...")
                self._safe_shutdown()
                time.sleep(2)
                self._connect_lidar()
            except Exception as e:
                print(f"[LIDAR Unexpected Error]: {e}")
                break

        self._safe_shutdown()

    def _safe_shutdown(self):
        try:
            if self.lidar:
                self.lidar.stop()
                self.lidar.disconnect()
                if self.debug:
                    print("[LIDAR] Stopped and disconnected.")
        except Exception as e:
            print(f"[LIDAR Shutdown Error]: {e}")

    def stop(self):
        self.running = False

    def process_scan(self, scan):
        front = left = right = False

        for _, angle, distance in scan:
            if 165 < angle < 195:
                if distance < self.front_thresh:
                    front = True
            elif 15 < angle < 90:
                if distance < self.left_thresh:
                    left = True
            elif 270 < angle < 345:
                if distance < self.right_thresh:
                    right = True

        self.front = front
        self.left = left
        self.right = right

    def get_obstacles(self):
        return self.front, self.left, self.right
