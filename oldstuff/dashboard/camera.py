from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("models/yolov8n.pt")


cam = cv2.VideoCapture(0) # change to correct camera (0 for webcam)

# Set the camera resolution (adjust based on your dashboard layout)
FRAME_WIDTH = 800   # Change to match dashboard width
FRAME_HEIGHT = 600  # Change to match dashboard height
cam.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

def generate_frames():
    while True:
        success, frame = cam.read()
        if not success:
            break


        # Resize the frame to match your dashboard's layout
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))


        # make frames lines only
        gray_image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        canny_image = cv2.Canny(gray_image, 100, 200)

        # get lines based on thresholds
        lines = cv2.HoughLinesP(
            canny_image,
            rho=6,
            theta=np.pi/60,
            threshold=160,
            lines=np.array([]),
            minLineLength=40,
            maxLineGap=25
        )


        results = model(frame)
        boxes = results[0].boxes

        for box in boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            #if model.names[cls] == 'car' and conf >= 0.5:
            if conf >= 0.5:
                label = f'{model.names[cls]} {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Encode frame to JPEG for Flask streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
