import cv2
import numpy as np

# zorgt dat alleen het nuttige gedeelte van de frame overblijft (niet de lucht enz)
def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

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
        region_vertices = [(0, height), (width // 2, height // 2), (width, height)] #links onder, midden, rechts boven
        roi = region_of_interest(edges, np.array([region_vertices], np.int32))

        lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 50, np.array([]), minLineLength=25, maxLineGap=300)
            # (image met mask, elke pixel checken, elke graden angle checken, placeholder voor output storage, 
            # minimum lengte van een lijn om gedetecteerd te worden, maximum lengte tussen lijnen om 1 lijn voor te stellen)

        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

        cv2.line(frame, (0,500), (1250,500), (0,255,0),5)

        cv2.imshow("Lane Detection", frame)

        # Wait for 1ms before showing the next frame, if 'q' is pressed, break the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close the display window
    capture.release()
    cv2.destroyAllWindows()

video_path = 'input.mp4'
detect_lanes(video_path)