import cv2
import argparse
import numpy as np

myColors = (255,255,0)

# Get names of output layers, output for YOLOv3 is ['yolo_16', 'yolo_23']
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Darw a rectangle surrounding the object and its class name 
def draw_pred(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), myColors, 5)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, myColors, 5)
    
# Define a window to show the cam stream on it
window_title= "Rubiks Detector"   
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)


# Load names classes
classes = None
with open("custom/obj.names", 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(classes)

#Generate color for each class randomly
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Define network from configuration file and load the weights from the given weights file
net = cv2.dnn.readNet("tiny-yolo_last.weights","custom/tiny-yolo.cfg")

# Define video capture for default cam
cap = cv2.VideoCapture(0)

while cv2.waitKey(1) < 0 or False:


    hasframe, image = cap.read()

    image=cv2.resize(image, (640, 480)) 
    #blob = cv2.dnn.blobFromImage(image, 1.0/255.0, (416,416), [0,0,0], True, crop=False)
    blob = cv2.dnn.blobFromImage(image, 1.0/255.0, (640,480), [0,0,0], True, crop=False)
    Width = image.shape[1]
    Height = image.shape[0]
    net.setInput(blob)
    
    outs = net.forward(getOutputsNames(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
      
    for out in outs: 
        for detection in out:
            
        #each detection  has the form like this [center_x center_y width height obj_score class_1_score class_2_score ..]
            scores = detection[5:]#classes scores starts from index 5
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    
    # apply non-maximum suppression algorithm on the bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_pred(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
   
    # Put efficiency information.
    t, _ = net.getPerfProfile()
    inferenceTime = 'Time process: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    FPS = 'FPS: %d ' % (cv2.getTickFrequency()/t)
    cv2.putText(image, inferenceTime, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, myColors,3)
    cv2.putText(image, FPS, (480, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, myColors,3)
    cv2.imshow(window_title, image)
