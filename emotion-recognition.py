import cv2
import os
import pandas as pd
from feat import Detector 
import csv 
import warnings
import numpy as np
import matplotlib.pyplot as plt

# to ignore all warnings
warnings.filterwarnings("ignore")

#initialize the detector
detector = Detector(device="cuda")

path_to_file = "..\DiffusionFER\DiffusionEmotion_S\dataset_sheet.csv"
csv_path='.\\aus.csv'

#load the annotations
dataset = pd.read_csv(path_to_file)

emotions_dict= {0 :'neutral',1:'happy',2:'sad',3:'surprise',4:'fear',5:'disgust',6:'angry'}

with open(csv_path, 'w',newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    header_row=['emotion','AU01','AU02','AU04','AU05','AU06','AU07','AU09','AU10','AU11','AU12','AU14','AU15','AU17','AU20','AU23','AU24','AU25','AU26','AU28','AU43']
    csv_writer.writerow(header_row)
    positive_emotion = {}
    negative_emotion = {}
    for em in header_row[1:]:
        positive_emotion[em] = []
        negative_emotion[em] = []
    
    for index, row in dataset.iterrows():
        image_path_end = row['subDirectory_filePath']
        expression = row['expression']
        valence= row['valence']

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


            #choose the correct data

            labels = dataset['valence']

            positive_data = dataset[labels >= 0]
            negative_data = dataset[labels < 0]

            au_idx = 0

            if len(aus[0]) != 0:
                for au in aus[0][0]:
                    au_name = header_row[au_idx+1]

                    if valence >= 0:
                        positive_emotion[au_name].append(au)
                    else:
                        negative_emotion[au_name].append(au)
                    au_idx += 1
                #print(positive_emotion)
                #change emotion from number to string with name
                row_data=[emotions_dict[expression]]+list(aus[0][0])
                csv_writer.writerow(row_data)
            else:
                print("Warning: no face detected")

    AU_mean_dif = {}
    for em in header_row[1:]:
        positive_mean = np.mean(positive_emotion[em])
        negative_mean = np.mean(negative_emotion[em])
        AU_mean_dif[em] = abs(positive_mean - negative_mean)
    
    sorted_au_names = dict(sorted(AU_mean_dif.items(), key=lambda item:item[1], reverse=True))


    plt.figure(figsize=(10, 6))
    plt.scatter(sorted_au_names.keys(), sorted_au_names.values(), color='skyblue', marker='o')
    plt.title('Absolute Difference of Means for AUs between Positive and Negative Conditions')
    plt.xlabel('AU')
    plt.ylabel('Absolute Difference of Means')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # save 
    plt.savefig('au_visualization.png')

    # show the graph
    plt.show()




