import pandas as pd
import cv2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from feat import Detector 

from joblib import dump
import warnings

# to ignore all warnings
warnings.filterwarnings("ignore")

AU_TO_DROP = ['AU11', 'AU25', 'AU09', 'AU04', 'AU02', 'AU23', 'AU15', 'AU01', 'AU05', 'AU28', 'AU26', 'AU17', 'AU24']
#AU_TO_DROP = ['AU11', 'AU25', 'AU09', 'AU04', 'AU02', 'AU23', 'AU15']

def read_and_preprocess(file_path):
    data = pd.read_csv(file_path)

    labels = data["emotion"]
    features = data.drop(['valence']+["emotion"] + AU_TO_DROP, axis=1)

    scaler = StandardScaler()
    features_standardized = scaler.fit_transform(features)

    return features_standardized, labels, scaler

def balanced_split(features, labels):
    # Split = 70/20/10
    data_in, test_in, data_out, test_out = train_test_split(
        features,
        labels,
        test_size=0.1,
        random_state=42,
        stratify=labels  
    )
    train_in, val_in, train_out, val_out = train_test_split(
        data_in,
        data_out,
        test_size=(0.2/0.9),  # 20% of the original data
        random_state=42,
        stratify=data_out
    )

    return train_in, val_in, test_in, train_out, val_out, test_out

def train_and_eval(model, train_in, train_out, val_in, val_out):
    model.fit(train_in, train_out)
    predicted_val = model.predict(val_in)

    # Evaluate model
    return accuracy_score(val_out, predicted_val)
def hyperparameter_tuning_svm(train_in, train_out, val_in, val_out):
    param_grid = [
        {'kernel': ['linear', 'poly', 'rbf', 'sigmoid']}
    ]

    svm_model = SVC()

    grid_search = GridSearchCV(svm_model, param_grid, cv=5, scoring='accuracy')
    grid_search.fit(train_in, train_out)

    best_svm_model = grid_search.best_estimator_
    print("Best SVM model: ", grid_search.best_params_)

    predicted_val_svm = best_svm_model.predict(val_in)

    # Evaluate the best model
    accuracy_svm = accuracy_score(val_out, predicted_val_svm)
    print("Accuracy of SVM model with best parameters on the validation set: ", accuracy_svm)

    return best_svm_model

def main():
    detector=Detector(device="cpu")

    file_path=".\database_management_emotions\\aus.csv"
    features, labels, scaler = read_and_preprocess(file_path)
    train_in, val_in, test_in, train_out, val_out, test_out = balanced_split(features, labels)


    model_svc = SVC()
    print(
        "\nAccuracy of model_svc: ",
        train_and_eval(model_svc, train_in, train_out, val_in, val_out)
    )

    best_svm_model = hyperparameter_tuning_svm(train_in, train_out, val_in, val_out)

    predicted_test_svm = best_svm_model.predict(test_in)

    # Evaluate the model on the test set
    accuracy_test_svm = accuracy_score(test_out, predicted_test_svm)
    print("Accuracy of SVM model on the test set: ", accuracy_test_svm*100)



    
    #tr
    #dump(best_svm_model, 'svm_model.joblib')

if __name__ == "__main__":
    main()