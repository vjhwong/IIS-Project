import cv2
import os
import pandas as pd
from feat import Detector  
import warnings
from joblib import load

emotion = ''
cap = None

def destroy_video():
    cap.release()
    cv2.destroyAllWindows()
    return emotion

def create_video():
    while True:
        # to ignore all warnings
        warnings.filterwarnings("ignore")

        model = load('svm_model.joblib')

        detector = Detector(device="cpu")

        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        if not ret:
            return None
        faces = detector.detect_faces(frame)
        landmarks = detector.detect_landmarks(frame, faces)
        aus = detector.detect_aus(frame, landmarks)
        emotion = model.predict(aus[0])
        face_idx = 0
        for (x, y, w, h, p) in faces[0]:
            cv2.rectangle(frame, (int(x), int(y)), (int(w), int(h)), (0, 0, 255), 3)
            cv2.putText(frame, emotion[face_idx], (int(x), int(y - 10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255),
                        2)
            face_idx += 1
        cv2.imshow("frame", frame)

def detect_emotion():
    return emotion
        




    
    

    

    