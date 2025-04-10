import cv2
import numpy as np

y_target = 500
x_target = 0 #standaard positie van de lijn bij y=500

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

        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        grayscale = cv2.inRange(gray, 200, 255) #200 - 255

        edges = cv2.Canny(grayscale, 50, 150)

        height, width = edges.shape
        
        #region_vertices = [(0, height // 2), (width, height // 2), (width, height), (0, height)] #onderkant
        # region_vertices = [(0, 0), (width, 0), (width, height // 2), (0, height // 2)] #bovenkant
        #roi = region_of_interest(edges, np.array([region_vertices], np.int32))
        #lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)
        
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)


        x_at_target_values = []

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    if x1 != x2 and y1 != y2:
                        x_at_target_values.append(get_x(line))
                        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

        if x_at_target_values:
            x_at_target = int(np.mean(x_at_target_values))
            if x_at_target < x_target - 50: #voorbeeld waardes
                print("steer left")
            elif x_at_target > x_target + 50: #voorbeeld waardes
                print("steer right")

        # cv2.imshow("Grayscale", grayscale)
        cv2.imshow("Lines", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

path = 'C:/Vakken/Jaar 2/Project 78 (SDC)/data/smalldemoright/output_video.mp4'
detect_lanes(path)