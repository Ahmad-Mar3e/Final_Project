import numpy as np
import joblib as jl
from sklearn.ensemble import RandomForestClassifier 

#specify data set path
Path_dataset = "Data_Set"

#Loadin saved features and their labels
x_train = np.load(f"{Path_dataset}/x_train.npy")
y_train = np.load(f"{Path_dataset}/y_train.npy")
x_test = np.load(f"{Path_dataset}/x_test.npy")
y_test = np.load(f"{Path_dataset}/y_test.npy")

from sklearn.preprocessing import StandardScaler

#Scalin before fittin
scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

#Specify the model
rf = RandomForestClassifier(n_estimators=1000, criterion= "entropy", max_depth=7, min_samples_split=6, min_samples_leaf=3, random_state=42, class_weight="balanced")
rf.fit(x_train, y_train)

#seein accuracy and performance
from sklearn.metrics import classification_report

y_pred = rf.predict(x_test)
print("Accuracy:",rf.score(x_test, y_test))

from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))

#Saving the trained model
jl.dump(rf, f"{Path_dataset}/On_Off_trainedModel.pkl")
jl.dump(scaler, f"{Path_dataset}/scaler.pkl")
print("Saved")