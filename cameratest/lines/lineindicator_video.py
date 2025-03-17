import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def get_x_at_ytarget(y_target, x1, y1, x2, y2):
    if y1 == y2:
        return None
    x_at_target = int(x1 + (((y_target - y1) * (x2 - x1) ) / (y2 - y1)))
    return x_at_target

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

        if lines is not None: #per frame
            for line in lines: #per line in het frame
                for x1, y1, x2, y2 in line:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

                    x_at_target = get_x_at_ytarget(y_target, x1, y1, x2, y2)
                    if x_at_target is not None:
                        if x_at_target < width // 2: #linker helft scherm
                            left_x_values.append(x_at_target)
                        else: #rechter helft scherm
                            right_x_values.append(x_at_target)

        if left_x_values and right_x_values:
            avg_x = int((np.mean(left_x_values) + np.mean(right_x_values)) / 2)
            cv2.line(frame, (avg_x, 490), (avg_x, 510), (255, 255, 0), 3)


        kart_middle_x = width / 2
        if kart_middle_x - 50 > avg_x:
            print("turn left")
        elif kart_middle_x + 50 < avg_x:
            print("turn right")


        cv2.imshow("Lane Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

video_path = 'input.mp4'
detect_lanes(video_path)