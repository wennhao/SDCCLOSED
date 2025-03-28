"""
word gerunt op rechter en linker camera

pakt een vast y coordinaat (500) op het scherm en kijkt waar de lijn op de x-as ligt

als verder naar links is dan een bepaalde x value: stuur naar rechts
als verder naar rechts is dan een bepaalde x value: stuur naar links


linker bocht (linker lijn volgen) initiatie
rij naar links totdat de op de linker camera de stuur statements aangeroepen worden

daarna als stuur angle rond 0 is dan terug naar rechter lijn
"""

import cv2
import numpy as np

y_target = 500
x_target = 0 # standaard positie van de lijn bij y=500

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_x(lines):
    for x1, y1, x2, y2 in lines:
        m = (x2 - x1) / (y2 - y1)
        x_coord = x1 + (y_target - y1) * m
        return int(x_coord)
    return None

def detect_lanes(path):
    capture = cv2.VideoCapture(path)

    if not capture.isOpened():
        print("Error: Could not open video.")
        return

    while True:
        ret, frame = capture.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        height, width = edges.shape
        region_vertices = [(0, height), (width // 2, height // 2), (width, height)]
        roi = region_of_interest(edges, np.array([region_vertices], np.int32))

        lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)

        x_at_target_values = []

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    if x1 != x2 and y1 != y2:
                        x_at_target_values.append(get_x(line)) # alleen als het bepaalde afstand heeft van x_target ?]

        if x_at_target_values:
            x_at_target = np.mean(x_at_target_values)
            if x_at_target < x_target - 50: # voorbeeld waardes
                print("steer left")
            elif x_at_target > x_target + 50: # voorbeeld waardes
                print("steer right")
            #hoe verder x_at_target van x_target vandaan is, hoe meer er wordt gestuurd
        print(x_at_target)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    capture.release()

# path = 'C:\\Vakken\\Project 78 (SDC)\\SDCCLOSED\\cameratest\\lines\\input.mp4'
path = 1
detect_lanes(path)