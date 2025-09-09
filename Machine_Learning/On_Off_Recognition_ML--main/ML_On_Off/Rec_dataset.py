import pyaudio
import wave
import os

# setting audio parameters
Format = pyaudio.paInt16
Channels = 1
Rate = 16000
Chunk = 1024 #Frame per Buffer
Record_Seconds = 3
Name = "Name"

#spicify saved path
Path_dataset = "Data_Set" #folder named data set inside it two folders On and Off write the specific path if it doesn't work

#function to record one_voice sample
def record(label, index):

    #saved file name
    file = f"{Path_dataset}/{label}/{Name}_{label}_{index}.wav"
    p = pyaudio.PyAudio()

    #Setting the data parameters in recording file
    stream = p.open(format= Format,
                channels= Channels,
                rate= Rate,
                input= True,
                frames_per_buffer= Chunk
                )
    
    #Recording process
    print("Recornding...")
    frames = [stream.read(Chunk) for i in range (int(Rate/Chunk*Record_Seconds))]
    print("Completed")

    #Stop the recording
    stream.stop_stream()
    stream.close()
    p.terminate()

    #Setting the recorded data in the file
    with wave.open(file, 'wb') as f:
        f.setnchannels(Channels)
        f.setsampwidth(p.get_sample_size(Format))
        f.setframerate(Rate)
        f.writeframes(b''.join(frames))

#main project
for label in ["On", "Off"]:
    os.makedirs(f"{Path_dataset}/{label}", exist_ok=True)

    #recording multiple audio 
    for index in range (1, 101):
        input(f"\nPress Enter and say {label}: ")
        record(label , index) 

for label in ["On_test", "Off_test"]:
    os.makedirs(f"{Path_dataset}/{label}", exist_ok=True)

    #recording multiple audio 
    for index in range (1, 21):
        input(f"\nPress Enter and say {label}: ")
        record(label , index)         

       

 