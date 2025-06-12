import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_y(line, x_norm):
    x1, y1, x2, y2 = line
    if x1 == x2:  # vertical line
        return y1
    if (x1 - x_norm) * (x2 - x_norm) > 0:  # line does not cross x_norm
        return None

    m = (y2 - y1) / (x2 - x1)
    y = y1 + (x_norm - x1) * m
    return int(y)

def process_frame(frame, direction):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.inRange(gray, 195, 255) #150

    edges = cv2.Canny(grayscale, 70, 200)

    height, width = edges.shape
    y_norm = int(height * 0.2)

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

    y_at_target_values = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            y_val = get_y([x1, y1, x2, y2], x_norm)
            if y_val is not None:
                y_at_target_values.append(y_val)
                
                #visualisation of the lines (not needed for tests)
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

    # Draw guidelines (visualisation of the lines (not needed for tests))
    cv2.line(frame, (x_norm - 100, y_norm), (x_norm + 100, y_norm), (255, 255, 0), 2) # y_norm
    cv2.line(frame, (x_norm, 0), (x_norm, height), (255, 255, 0), 2) # x_norm
    cv2.line(frame, (roi_border_x, 0), (roi_border_x, height), (0, 255, 255), 2) # ROI

    threshold1 = 25
    threshold2 = 100
    cv2.line(frame, (x_norm - 10, y_norm - threshold1), (x_norm + 10, y_norm - threshold1), (255,255,0), 2)
    cv2.line(frame, (x_norm - 10, y_norm - threshold2), (x_norm + 10, y_norm - threshold2), (255,255,0), 2)
    cv2.line(frame, (x_norm - 10, y_norm + threshold1), (x_norm + 10, y_norm + threshold1), (255,255,0), 2)
    cv2.line(frame, (x_norm - 10, y_norm + threshold2), (x_norm + 10, y_norm + threshold2), (255,255,0), 2)
    
    if y_at_target_values:
        y_at_target = int(np.median(y_at_target_values))
        
        #visualisation of the lines (not needed for tests)
        cv2.circle(frame, (x_norm, y_at_target), 8, (255, 0, 0), -1)
        if direction == "RIGHT": 
            if y_at_target < y_norm - 100:
                return "turning_right_sharp", frame # 1.2
            elif y_at_target > y_norm + 100:
                return "turning_left_sharp", frame # (-1.2)
            elif y_at_target < y_norm - 25:
                return "turning_right", frame # 0.65
            elif y_at_target > y_norm + 25:
                return "turning_left", frame # (-0.65)
            else:
                return "driving_straight", frame # 0.0
        elif direction == "LEFT":
            if y_at_target < y_norm - 100:
                return "turning_left_sharp", frame # (-1.2)
            elif y_at_target > y_norm + 100:
                return "turning_right_sharp", frame # 1.2
            elif y_at_target < y_norm - 25:
                return "turning_left", frame # (-0.65)
            elif y_at_target > y_norm + 25:
                return "turning_right", frame # 0.65
            else:
                return "driving_straight", frame # 0.0
    else:
        return "searching_lane", frame