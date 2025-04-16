import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_x(line, y_norm):
    x1, y1, x2, y2 = line
    if x1 == x2:  # vertical line
        return x1
    if (y1 - y_norm) * (y2 - y_norm) > 0: # line does not cross y_norm
        return None

    m = (y2 - y1) / (x2 - x1)
    if m == 0:
        return None
    x = x1 + (y_norm - y1) / m
    return int(x)


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
        grayscale = cv2.inRange(gray, 150, 255) # 200 - 255 voor rechter camera

        edges = cv2.Canny(grayscale, 70, 200)

        height, width = edges.shape
        y_norm = int(height / 2)
        x_norm = 600

        region_vertices = [(width // 2, 0), (width, 0), (width, height), (width // 2, height)] # rechterkant
        roi = region_of_interest(edges, np.array([region_vertices], np.int32))
        lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)

        x_at_target_values = []

        x_at_target_values = []

        if lines is not None:
            for line in lines:
                x_val = get_x(line[0], y_norm)
                if x_val is not None:
                    x_at_target_values.append(x_val)
                    x1, y1, x2, y2 = line[0]
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

        if x_at_target_values:
            x_at_target = int(np.median(x_at_target_values))
            cv2.circle(frame, (x_at_target, y_norm), 10, (255, 0, 0), -1)  # visualisation of x_at_target
            if x_at_target < x_norm - 50: # example values
                print("steer left")
            elif x_at_target > x_norm + 50: # example values
                print("steer right")
            else:
                print("go straight")    

        cv2.line(frame, (0, y_norm), (width, y_norm), (255, 255, 0), 2) # y_norm
        cv2.line(frame, (x_norm, 0), (x_norm, height), (255, 255, 0), 2) # x_norm
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 255), 2) # ROI
        
        #cv2.imshow("Grayscale", grayscale)
        cv2.imshow("Lines", frame)

        if cv2.waitKey(33) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

path = 'C:/Vakken/Jaar 2/Project 78 (SDC)/data/smalldemofront/output_video.mp4'
detect_lanes(path)