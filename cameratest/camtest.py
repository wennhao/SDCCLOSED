from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO('yolov8n.pt')
model.export(format='openvino') # export in openvino format
ov_model = YOLO('yolov8n_openvino_model/') # load the exported openvino model

#cam = cv2.VideoCapture(0) # change to camera index

cam = cv2.VideoCapture('nlroad.mp4')
ret, frame = cam.read()

while ret:
    ret, frame = cam.read()
    if not ret:
        break

    # reduce quality based on fx and fy
    frame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)

    ### LINE DETECTION

    # make grayscale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # slightly blur
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)

    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # H: 0-179
    # S: 0-255
    # B: 0-255
    #low = np.array([0, 0, 160])
    #high = np.array([179, 100, 255])
    #mask_line_image = cv2.inRange(hsv, low, high)

    canny_image = cv2.Canny(blurred, 75, 150)

    mask = np.zeros_like(canny_image)
    height = mask.shape[0]
    width = mask.shape[1]
    center_x = width//2
    center_y = height//2 + 250
    top_width = 200
    bottom_width = 1000
    mask_height = 300
    roi = np.array([[(center_x+bottom_width//2, center_y+mask_height//2), (center_x-bottom_width//2, center_y+mask_height//2), (center_x-top_width//2, center_y-mask_height//2), (center_x+top_width//2, center_y-mask_height//2)]], dtype=np.int32)
    #roi = np.array([[(center_x+500, center_y+500), (center_x-500, center_y+500), (center_x-500, center_y-500), (center_x+500, center_y-500)]], dtype=np.int32)
    #height_offset = -120 # offset center (horizon)
    #top_width = 100 # top width
    #bottom_width = 650 # road width at bottom
    #width_offset = -20 # center road
    #roi = np.array([[(width//2+width_offset-bottom_width//2, height), (width//2+width_offset-top_width//2, height//2 - height_offset), (width//2+width_offset+top_width//2, height//2 - height_offset), (width//2+width_offset+bottom_width//2, height)]], dtype=np.int32)
    cv2.fillPoly(mask, roi, 255)
    masked_image = cv2.bitwise_and(canny_image, mask)

    # get lines based on thresholds
    lines = cv2.HoughLinesP(
        masked_image,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        lines=np.array([]),
        minLineLength=70,
        maxLineGap=50
    )

    # fill polygons for lanes (needs mask)
    polygon_points = []
    line_image = frame
    linepoints = []
    if lines is not None:
        for line in lines:
            polygon_points.append((line[0][0], line[0][1]))
            polygon_points.append((line[0][2], line[0][3]))

            linepoints.append([line[0][0], line[0][1]])
            linepoints.append([line[0][2], line[0][3]])
    
    if len(polygon_points) > 0:
        polygon_points = np.array(polygon_points, dtype=np.int32).reshape((-1, 1, 2))

        line_image = cv2.fillPoly(frame, [polygon_points], color=(0, 255, 0))


    ### OBJECT DETECTION
    results = ov_model(frame)
    boxes = results[0].boxes

    for box in boxes:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        #if model.names[cls] == 'car' and conf >= 0.5:
        if conf >= 0.5:
            label = f'{model.names[cls]} {conf:.2f}'
            #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            #cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    average = [0, 0]
    for point in linepoints:
        average[0] += point[0]
        average[1] += point[1]
    
    if len(linepoints) > 0:
        average = [int(average[0]/len(linepoints)), int(average[1]/len(linepoints))]
        #frame = cv2.rectangle(frame, (average[0]-50, average[1]+50), (average[0]+50, average[1]-50), (0, 0, 255), 5)

    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) == ord('q'):
        break