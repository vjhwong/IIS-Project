import cv2
import os
import pandas as pd
from feat import Detector 
import csv 
import warnings

# to ignore all warnings
warnings.filterwarnings("ignore")

#initialize the detector
detector = Detector(device="cuda")

path_to_file = "..\DiffusionFER\DiffusionEmotion_S\dataset_sheet.csv"
csv_path='.\\aus.csv'

#load the annotations
dataset = pd.read_csv(path_to_file)

emotions_dict= {'0':'neutral','1':'happy','2':'sad','3':'surprise','4':'fear','5':'disgust','6':'angry'}

with open(csv_path, 'w',newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    header_row=['emotion','AU01','AU02','AU04','AU05','AU06','AU07','AU09','AU10','AU11','AU12','AU14','AU15','AU17','AU20','AU23','AU24','AU25','AU26','AU28','AU43']
    csv_writer.writerow(header_row)
    for index, row in dataset.iterrows():
        image_path_end = row['subDirectory_filePath']
        expression = row['expression']

        image_path = os.path.join('..\DiffusionFER\DiffusionEmotion_S', image_path_end)

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


            #change emotion from number to string with name
            if len(aus[0]) != 0:
                row_data=[emotions_dict[expression]]+list(aus[0][0])
                csv_writer.writerow(row_data)
            else:
                print("Warning: no face detected")
            

