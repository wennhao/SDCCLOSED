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

def process_frame(frame, direction):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.inRange(gray, 150, 255) #150

    edges = cv2.Canny(grayscale, 70, 200)

    height, width = edges.shape
    y_norm = int(height / 2)

    if direction == "RIGHT":
        x_norm = int(540/848 * width)

        roi_border_x = int(width / 8 * 3)
        region_vertices = [(roi_border_x, 0), (width, 0), (width, height), (roi_border_x, height)] # rechterkant

    elif direction == "LEFT":
        x_norm = int(540/848 * width - 0.5*width)

        roi_border_x = int(width / 8 * 5)
        region_vertices = [(roi_border_x, 0), (0, 0), (0, height), (roi_border_x, height)] # linkerkant

    
    roi = region_of_interest(edges, np.array([region_vertices], np.int32))
    lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=50, maxLineGap=300)

    x_at_target_values = []

    if lines is not None:
        for line in lines:
            x_val = get_x(line[0], y_norm)
            if x_val is not None:
                x_at_target_values.append(x_val)
                
                #visualisation of the lines (not needed for tests)
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

    # Draw guidelines (visualisation of the lines (not needed for tests))
    cv2.line(frame, (0, y_norm), (width, y_norm), (255, 255, 0), 2)
    cv2.line(frame, (x_norm, 0), (x_norm, height), (255, 255, 0), 2)
    cv2.line(frame, (roi_border_x, 0), (roi_border_x, height), (0, 255, 255), 2)
    print("Detected lane x-values:", x_at_target_values)

    if x_at_target_values:
        x_at_target = int(np.median(x_at_target_values))
        
        #visualisation of the lines (not needed for tests)
        cv2.circle(frame, (x_at_target, y_norm), 8, (255, 0, 0), -1) 

        if x_at_target < x_norm - 100:
            return "turning_left_sharp", frame # (-1.2)
        elif x_at_target > x_norm + 100:
            return "turning_right_sharp", frame # 1.2
        elif x_at_target < x_norm - 25:
            return "turning_left", frame # (-0.65)
        elif x_at_target > x_norm + 25:
            return "turning_right", frame # 0.65
        else:
            return "driving_straight", frame # 0.0
    else:
        return "searching_lane", frame