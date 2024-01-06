import time

import cv2
import os
import pandas as pd
from feat import Detector  
import warnings
import threading, queue

cap = None

AU_TO_DROP = ['AU11', 'AU26', 'AU24', 'AU28', 'AU10', 'AU09', 'AU04', 'AU17', 'AU02', 'AU05', 'AU23', 'AU15', 'AU01']
header_row = ['AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 'AU11', 'AU12', 'AU14', 'AU15',
              'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 'AU26', 'AU28', 'AU43']

#AU_TO_KEEP = [12,6,43,14,7,20,25]
AU_TO_KEEP = [4,5,9,10,13,16,19]
STOP = 'STOP'

def destroy_video():
    cap.release()
    cv2.destroyAllWindows()

def create_video(queue : queue.Queue, model):
    stopped = False

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

        # tried to separate feature recognition and emotion prediciton but if we show the emotion in the video, we cannot do that
        # second zero index is for first face
        # emotion = model.predict([aus[i] for i in AU_TO_KEEP] for aus in aus[0])
        emotion = model.predict([[aus[0][0][i] for i in AU_TO_KEEP]])

        with lock:
            while not queue.empty():
                top = queue.get()
                if top == STOP:
                    stopped = True
                    break
            queue.queue.clear()
            # modify the global variable
            #queue.put(aus[0])
            queue.put(emotion)

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
        




    
    

    

    