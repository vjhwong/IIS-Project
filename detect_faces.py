import cv2
import os
import pandas as pd
from feat import Detector  
import warnings
from joblib import load

# to ignore all warnings
warnings.filterwarnings("ignore")

model=load('svm_model.joblib')

detector = Detector(device="cpu")

cap = cv2.VideoCapture(0)
recording = False
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if recording:
        faces = detector.detect_faces(frame)
        landmarks = detector.detect_landmarks(frame, faces)
        aus = detector.detect_aus(frame, landmarks)
        test_output = model.predict(aus[0])
        face_idx = 0
        for (x, y, w, h, p) in faces[0]:
            cv2.rectangle(frame, (int(x), int(y)), (int(w), int(h)), (0, 0, 255), 3)
            cv2.putText(frame, test_output[face_idx], (int(x), int(y - 10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
            face_idx+=1
        cv2.circle(frame, (20,20), 10, (0,0,255), -1)
    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    if key == ord(' '):
        recording = not recording
    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()



    
    

    

    