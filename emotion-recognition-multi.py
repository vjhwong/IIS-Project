import cv2
import os
from feat import Detector
import csv
import warnings
import numpy as np
import matplotlib.pyplot as plt

# to ignore all warnings
warnings.filterwarnings("ignore")

# initialize the detector
detector = Detector(device="cuda")

main_folder = "..\MultiEmoVA"

csv_path = '.\\ausMulti.csv'

# create a list to store file paths
image_paths = []

emotion_labels = ["anger", "disgust", "fear", "happiness", "neutral", "sadness", "surprise"]

#get the image paths
for root, dirs, files in os.walk(main_folder):
    for file in files:
        if file.endswith(('.jpg', '.jpeg', '.png')):  
            image_paths.append(os.path.join(root, file))

with open(csv_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    header_row = ['file','idx','emotion', 'AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 'AU11', 'AU12', 'AU14',
                  'AU15', 'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 'AU26', 'AU28', 'AU43']
    csv_writer.writerow(header_row)

    for image_path in image_paths:
        print(f"Processing image: {image_path}")
        if not os.path.exists(image_path):
            print(f"Warning: Image file not found: {image_path}")
        else:
            # load the image
            image = cv2.imread(image_path)

            # analyze the image
            faces = detector.detect_faces(image)
            landmarks = detector.detect_landmarks(image, faces)
            emotions = detector.detect_emotions(image, faces, landmarks)
            aus = detector.detect_aus(image, landmarks)

            aus_array = aus[0].tolist()
            

            for a, emotion_probs in zip(faces, emotions):
                for i,face in enumerate(a):
                    print(f"Processing face: {i}")
                    print(f"Face coordinates: {face}")
                    #get and write the emotion
                    max_emotion_index = emotion_probs[i].argmax()
                    emotion_label = emotion_labels[max_emotion_index]

                    # write the aus
                    aus_now = aus_array[i]
                    csv_writer.writerow([image_path]+[i]+[emotion_label] + list(aus_now))
                    

    
