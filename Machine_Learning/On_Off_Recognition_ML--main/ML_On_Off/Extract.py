import librosa
import numpy as np
import os

# specify data set path
Path_dataset = "Data_Set"

# Function to extract voice data from file
def extract(file): 
    audio_data, sample_rate = librosa.load(file, sr=16000)

    # Apply pre-emphasis filter
    audio_data = librosa.effects.preemphasis(audio_data)

    # Trim silence
    audio_data, _ = librosa.effects.trim(audio_data)

    # ---- MFCC features ----
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
    delta = librosa.feature.delta(mfccs)
    delta2 = librosa.feature.delta(mfccs, order=2)
    features = np.vstack([mfccs, delta, delta2])  # shape (39, frames)

    #Mean + Std 
    mfccs_mean = np.mean(features.T, axis=0)
    mfccs_std = np.std(features.T, axis=0)

    #Extra features: energy, zcr, pitch
    rms = np.mean(librosa.feature.rms(y=audio_data))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=audio_data))
    pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
    pitch_mean = np.mean(pitch[pitch > 0]) if np.any(pitch > 0) else 0

    #Final vector
    feat = np.concatenate([mfccs_mean, mfccs_std, [rms, zcr, pitch_mean]])
    return feat


# lists for train_data (features+labels)
features_List_train = []
labels_List_train = []

# lists for test_data (features+labels)
features_List_test = []
labels_List_test = []

# Extract features and adding them in list + adding labels for training
for label in ["On", "Off"]:
    folder = os.path.join(Path_dataset, label)
    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        features = extract(filepath)
        features_List_train.append(features)
        labels_List_train.append(1 if label == "On" else 0) 

# Extract features and adding them in list + adding labels for testing
for label_1 in ["On_test", "Off_test"]:
    folder_1 = os.path.join(Path_dataset, label_1)
    for file_1 in os.listdir(folder_1):
        filepath_1 = os.path.join(folder_1, file_1)
        features_1 = extract(filepath_1)
        features_List_test.append(features_1)
        labels_List_test.append(1 if label_1 == "On_test" else 0)

# features_List transformed to numpy array
x_train = np.array(features_List_train)
x_test = np.array(features_List_test)

# labels_List transformed to numpy array
y_train = np.array(labels_List_train)  
y_test = np.array(labels_List_test)

# Save arrays for future use
np.save(f"{Path_dataset}/x_train.npy", x_train)
np.save(f"{Path_dataset}/y_train.npy", y_train)
np.save(f"{Path_dataset}/x_test.npy", x_test)
np.save(f"{Path_dataset}/y_test.npy", y_test)

# check that all works correctly
print("x_train.shape:", x_train.shape)  
print("y_train.shape:", y_train.shape)
print("x_test.shape:", x_test.shape)  
print("y_test.shape:", y_test.shape)
