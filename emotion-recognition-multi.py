import cv2
import os
from feat import Detector
import csv
import warnings
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
    header_row = ['file','face','valence','emotion', 'AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 'AU11', 'AU12', 'AU14',
                  'AU15', 'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 'AU26', 'AU28', 'AU43']
    csv_writer.writerow(header_row)

    for image_path in image_paths:
        #print(f"Processing image: {image_path}")
        if not os.path.exists(image_path):
            print(f"Warning: Image file not found: {image_path}")
        else:
            # Extract subfolder name
            subfolder_name = os.path.basename(os.path.dirname(image_path))

            # Determine positive or negative based on subfolder name
            if 'Positive' in subfolder_name:
                valence = 1  # Positive
            elif 'Negative' in subfolder_name:
                valence = -1  # Negative
            else:
                valence = 0  # Neutral or unknown

            #print("valence: ", valence)
            
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
                    #print(f"Processing face: {i}")
                    #print(f"Face coordinates: {face}")
                    #get and write the emotion
                    max_emotion_index = emotion_probs[i].argmax()
                    emotion_label = emotion_labels[max_emotion_index]

                    # write the aus
                    aus_now = aus_array[i]
                    csv_writer.writerow([image_path]+[i]+[valence]+[emotion_label] + list(aus_now))


data=pd.read_csv(csv_path)

labels=data['valence']

positive_data = data[labels>= 0]
negative_data = data[labels == -1]

#print(positive_data)

au_names = ['AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 'AU11', 'AU12', 'AU14', 'AU15', 'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 'AU26', 'AU28', 'AU43']

positive_means = positive_data.groupby('face')[au_names].mean()
negative_means = negative_data.groupby('face')[au_names].mean()


absolute_diff = np.abs(positive_means - negative_means)
mean_absolute_diff = absolute_diff.mean()

# sort based on mean absolute difference
sorted_au_names = sorted(au_names, key=lambda x: mean_absolute_diff[x], reverse=True)

# plot 
plt.figure(figsize=(10, 6))
plt.scatter(sorted_au_names, [mean_absolute_diff[au] for au in sorted_au_names], color='skyblue', marker='o')
plt.title('Absolute Difference of Means for AUs between Positive and Negative Conditions')
plt.xlabel('AU')
plt.ylabel('Absolute Difference of Means')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# save 
plt.savefig('au_visualizationMulti.png')

# show the graph
plt.show()


                    

    
