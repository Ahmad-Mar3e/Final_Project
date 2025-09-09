def run_voice_command(self):

    import pyaudio
    import joblib as jl
    import wave
    import librosa
    import numpy as np

    #Loadin ML model + scaler model
    rf = jl.load("On_Off_trainedModel.pkl")
    scaler= jl.load("scaler.pkl")
    print("Model's been Loaded")

    #Change it to the folder path before using
    Path_dataset = "Data_Set"   

    # setting audio parameters
    Format = pyaudio.paInt16
    Channels = 1
    Rate = 16000
    Chunk = 1024
    Record_Seconds = 3

    #Recordin audio
    p = pyaudio.PyAudio()

    stream = p.open(rate=Rate, channels=Channels, format=Format, input=True)

    messagebox.showinfo("Voice Command", "Start?")
    frames = [stream.read(Chunk) for i in range (int(Rate/Chunk*Record_Seconds))]
    messagebox.showinfo("Voice Command", "Done")

    file = f"{Path_dataset}/Output.wav"

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(file, 'wb') as f:
        f.setnchannels(Channels)
        f.setsampwidth(p.get_sample_size(Format))
        f.setframerate(Rate)
        f.writeframes(b''.join(frames))


    # Extracting features from the audio
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

    # ---- Mean + Std ----
    mfccs_mean = np.mean(features.T, axis=0)
    mfccs_std = np.std(features.T, axis=0)

    # ---- Extra features: RMS, ZCR, Pitch ----
    rms = np.mean(librosa.feature.rms(y=audio_data))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=audio_data))
    pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
    pitch_mean = np.mean(pitch[pitch > 0]) if np.any(pitch > 0) else 0

    # ---- Final feature vector (81 features) ----
    final_features = np.concatenate([mfccs_mean, mfccs_std, [rms, zcr, pitch_mean]])

    # Save features in an array
    features_list = []
    features_list.append(final_features)
    x_test_output = np.array(features_list)


    from sklearn.preprocessing import StandardScaler

    #Scalin the new output to be similar to traini data 
    x_test_output = scaler.transform(x_test_output)

    #Prediction point
    probs = rf.predict_proba(x_test_output)[0]
    prediction = rf.predict(x_test_output)[0]
    confidence = max(probs)

    return prediction, probs, confidence

def mic(self):
    prediction, probs, confidence = self.run_voice_command()
 
    #Check probability of being on or off
    if confidence < 0.6:
        messagebox.showwarning("Voice Command", "Not clear, please speak again.")
        return
    # ON condition
    if prediction == 1:  
            self.on_off_var.set("ON")
            self.current_state = "ON"
            messagebox.showinfo("Voice Command", "System Turned ON by voice!")
    # OFF condition        
    else:  
        self.on_off_var.set("OFF")
        self.current_state = "OFF"
        messagebox.showinfo("Voice Command", "System Turned OFF by voice!")
        if self.is_connected:
            self.disconnect_serial()