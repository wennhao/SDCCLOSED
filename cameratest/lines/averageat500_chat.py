import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_x_at_y(y_target, x1, y1, x2, y2):
    """ Returns the x-coordinate where the line (x1, y1) to (x2, y2) crosses y = y_target. """
    if y1 == y2:  # Avoid division by zero
        return None
    x_at_y = int(x1 + (y_target - y1) * (x2 - x1) / (y2 - y1))
    return x_at_y

def detect_lanes(video_path):
    capture = cv2.VideoCapture(video_path)
    
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

        lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=25, maxLineGap=300)

        left_x_values = []
        right_x_values = []
        y_target = 500

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)  # Draw detected lines

                    # Find x where the line crosses y = 500
                    x_at_500 = get_x_at_y(y_target, x1, y1, x2, y2)
                    if x_at_500 is not None:
                        if x_at_500 < width // 2:
                            left_x_values.append(x_at_500)
                        else:
                            right_x_values.append(x_at_500)

        # Compute average x and draw vertical line if both sides detected
        if left_x_values and right_x_values:
            avg_x = int((np.mean(left_x_values) + np.mean(right_x_values)) / 2)
            cv2.line(frame, (avg_x, 480), (avg_x, 520), (255, 255, 0), 3)  # Vertical guide line

        cv2.imshow("Lane Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

video_path = 'input.mp4'
detect_lanes(video_path)