import cv2
import os
import pandas as pd
from feat import Detector  
import warnings

# to ignore all warnings
warnings.filterwarnings("ignore")

#initialize the detector
detector = Detector(device="cuda")

cap = cv2.VideoCapture(0)
recording = False
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if recording:
        faces = detector.detect_faces(frame)
        landmarks = detector.detect_landmarks(frame, faces)
        emotions = detector.detect_emotions(frame, faces, landmarks)
        aus = detector.detect_aus(frame, landmarks)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.circle(frame, (20,20), 10, (0,0,255), -1)
    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    if key == ord(' '):
        recording = not recording
    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


    
    

    

    