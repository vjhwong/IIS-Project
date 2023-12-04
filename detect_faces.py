import time

import cv2
import os
import pandas as pd
from feat import Detector  
import warnings
import threading, queue

cap = None
stopped = False

def destroy_video():
    cap.release()
    cv2.destroyAllWindows()

def stop():
    stopped = True

def create_video(queue : queue.Queue, model):
    lock = threading.Lock()
    # to ignore all warnings
    warnings.filterwarnings("ignore")

    detector = Detector(device="cpu")

    cap = cv2.VideoCapture(0)

    while not stopped:
        ret, frame = cap.read()
        if not ret:
            return None
        faces = detector.detect_faces(frame)
        landmarks = detector.detect_landmarks(frame, faces)
        aus = detector.detect_aus(frame, landmarks)

        if(len(aus[0]) == 0):
            continue

        with lock:
            queue.queue.clear()
            # modify the global variable
            queue.put(aus[0])

        # tried to separate feature recognition and emotion prediciton but if we show the emotion in the video, we cannot do that
        emotion = model.predict(aus[0])
        face_idx = 0
        for (x, y, w, h, p) in faces[0]:
            cv2.rectangle(frame, (int(x), int(y)), (int(w), int(h)), (0, 0, 255), 3)
            cv2.putText(frame, emotion[face_idx], (int(x), int(y - 10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255),2)
            face_idx += 1
        print(emotion, flush=True)
        cv2.imshow("frame", frame)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
        




    
    

    

    