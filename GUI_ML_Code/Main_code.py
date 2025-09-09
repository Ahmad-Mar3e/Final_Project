import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import threading
import time
import pandas as pd
from datetime import datetime

"""
Received Data Format: TEMP:25.5,LIGHT:850,OBJECT:0
"""

class Ground_Station:
    def __init__(self):
        # Initializing Connection
        self.serial_conn = None
        self.is_connected = False
        self.data_thread = None
        self.stop_thread = False
        # Initializing Sensor Data
        self.data_file = "sensor_data.csv"
        self.load_historical_data() # Load existing data if available
        #Initializing GUI
        self.GUI()

    def load_historical_data(self):
        # If File Exists
        try:
            self.historical_data = pd.read_csv(self.data_file)
            print(f"Loaded {len(self.historical_data)} historical records")
        # If file not created yet
        except FileNotFoundError:
            print("No existing data file found!")
            self.historical_data = pd.DataFrame(columns=['timestamp', 'temperature', 'light_intensity', 'object_detected'])

    def GUI(self):
        self.root = tk.Tk()
        self.root.title("Ground Station")

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))
        self.root.configure(background="White")
        
        main_container = tk.Frame(self.root, background="White", width=width, height=height)
        main_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.root, text="Ground Station", font=('Arial', 36, "bold"), fg="Black", bg="White").pack(pady=50)
        
        # Left frame for satellite image
        left_frame = tk.Frame(main_container, width=width//2, background="White")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Right frame for other widgets
        right_frame = tk.Frame(main_container, background="White")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        try:
            self.original_image = Image.open("satellite.png")
            original_width, original_height = self.original_image.size
            
            frame_width = (width // 2) - 10
            new_height = int((frame_width * original_height) / original_width)
            
            resized_img = self.original_image.resize((frame_width, new_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_img)
            
            logo_label = tk.Label(left_frame, image=self.logo_image, background="White")
            logo_label.pack(pady=20)
            
        except:
            logo_label = tk.Label(left_frame, text="Satellite Image", bg='lightgray', font=("Arial", 16), width=20, height=10)
            logo_label.pack(pady=20)

        # Left Frame:
        # Voice Frame
        self.voice_frame = tk.Frame(right_frame, relief=tk.GROOVE, borderwidth=2, background="White")
        self.voice_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(self.voice_frame, text="Voice Command", font=("Arial", 18), background="White").pack(side=tk.TOP, pady=5)

        # Control Frame
        self.control_frame = tk.Frame(right_frame, relief=tk.GROOVE, borderwidth=2, background="White")
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(self.control_frame, text="System Control", font=("Arial", 18), background="White").pack(side=tk.TOP, pady=5)

        # Sensor Readings Frame
        self.sensor_frame = tk.Frame(right_frame, relief=tk.GROOVE, borderwidth=2, background="White")
        self.sensor_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(self.sensor_frame, text="Sensor Readings", font=("Arial", 18), background="White").pack(side=tk.TOP, pady=5)

        # Status Frame
        self.status_frame = tk.Frame(right_frame, background="White")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Voice Frame Content
        voice_content = tk.Frame(self.voice_frame, background="White")
        voice_content.pack(expand=True, fill=tk.BOTH, pady=10)
        voice_content.columnconfigure(0, weight=1)
        voice_content.columnconfigure(1, weight=1)
        
        self.on_off_var = tk.StringVar(value="ON / OFF")
        self.current_state = "OFF"
        status_label = tk.Label(voice_content, textvariable=self.on_off_var, font=("Arial", 14), background="White")
        status_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        try:
            mic_image = tk.PhotoImage(file="mic.png").subsample(5, 5)
            self.mic_button = tk.Button(voice_content, image=mic_image, command=self.mic)
            self.mic_button.image = mic_image
        except:
            self.mic_button = tk.Button(voice_content, text="MIC", command=self.mic, font=("Arial", 14))
        
        self.mic_button.grid(row=0, column=1, padx=5, pady=5)

        # Control Frame Content
        control_content = tk.Frame(self.control_frame, background="White")
        control_content.pack(expand=True, fill=tk.BOTH, pady=10)
    
        for i in range(4):
            control_content.columnconfigure(i, weight=1)
        
        # Modified to use connect_serial instead of connect_bluetooth
        self.connect_btn = tk.Button(control_content, text="Connect", font=("Arial", 14), bg="White", 
                command=self.connect_serial)
        self.connect_btn.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.disconnect_btn = tk.Button(control_content, text="Disconnect", font=("Arial", 14), bg="White",
                command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        number_records = [10, 25, 50, 100]
        self.cb = ttk.Combobox(control_content, values=number_records, width=22, state='readonly', font=('Arial', 14))
        self.cb.set("Select Number of Records")
        
        self.historical_data_btn = tk.Button(control_content, text="Get Historical Data", font=("Arial", 14), bg="White",
                command=lambda: self.view_historical_data_table(self.cb.get()))
        self.historical_data_btn.grid(row=0, column=2, sticky="ew", padx=10, pady=5)
        
        self.cb.grid(row=0, column=3, sticky="ew", padx=10, pady=5)

        # Sensor Readings Frame Content
        sensor_content = tk.Frame(self.sensor_frame, bg="White")
        sensor_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        sensor_content.columnconfigure(1, weight=1)
        
        # Temperature
        ttk.Label(sensor_content, text="Temperature:", font=("Arial", 14), background="White").grid(row=0, column=0, sticky="w", pady=5)
        self.temp_var = tk.StringVar(value="N/A °C")
        ttk.Label(sensor_content, textvariable=self.temp_var, font=("Arial", 14), background="White").grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Light intensity
        ttk.Label(sensor_content, text="Light Intensity:", font=("Arial", 14), background="White").grid(row=1, column=0, sticky="w", pady=5)
        self.light_var = tk.StringVar(value="N/A")
        ttk.Label(sensor_content, textvariable=self.light_var, font=("Arial", 14), background="White").grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Object detection
        ttk.Label(sensor_content, text="Object Detection:", font=("Arial", 14), background="White").grid(row=2, column=0, sticky="w", pady=5)
        self.object_var = tk.StringVar(value="No Objects Detected")
        ttk.Label(sensor_content, textvariable=self.object_var, font=("Arial", 14), background="White").grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Status Frame Content
        status_content = tk.Frame(self.status_frame, bg="White")
        status_content.pack(fill=tk.BOTH, expand=True)
        status_content.columnconfigure(1, weight=1) 
        
        ttk.Label(status_content, text="Status:", font=("Arial", 14), background="White").grid(row=0, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(status_content, textvariable=self.status_var, font=("Arial", 14), 
                  background="White", foreground="red").grid(row=0, column=1, sticky="w", padx=10)   

        self.root.mainloop()

    # Connect automatically without selecting the port manually
    def connect_serial(self):
        
        try:
            ports = serial.tools.list_ports.comports()
            
            microcontroller_port = None
            
            # Common identifiers for microcontroller boards
            common_identifiers = ["STM32", "STMicroelectronics", "USB Serial Device", "CH340", "CP210", "Arduino", "USB2.0-Serial"]
            
            print("Checking ports")
            for port in ports:
                for identifier in common_identifiers:
                    if identifier.lower() in port.description.lower():
                        microcontroller_port = port.device
                        print(f"Found potential microcontroller at: {microcontroller_port}")
                        break
                if microcontroller_port:
                    break
            
            # If no specific identifier found, try the first available port
            if not microcontroller_port and ports:
                microcontroller_port = ports[0].device
                print(f"Using first available port: {microcontroller_port}")
            
            if not microcontroller_port:
                messagebox.showerror("Error", "No serial devices found. Please connect your microcontroller.")
                return
            
            # Connect to the detected port
            self.serial_conn = serial.Serial(
                port=microcontroller_port, 
                baudrate=9600,  # Match your microcontroller's baud rate
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, 
                bytesize=serial.EIGHTBITS,
                timeout=0.1
            )
            
            self.is_connected = True
            self.status_var.set(f"Connected to {microcontroller_port}")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
            # Start a thread for receiving data
            self.stop_thread = False
            self.data_thread = threading.Thread(target=self.receive_data)
            self.data_thread.daemon = True
            self.data_thread.start()
            
            messagebox.showinfo("Success", f"Connected to {microcontroller_port} successfully!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")

    def disconnect_serial(self):
        
        self.stop_thread = True
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except:
                pass
            self.serial_conn = None
        
        self.is_connected = False
        self.status_var.set("Disconnected")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        
        # Reset sensor readings
        self.temp_var.set("N/A °C")
        self.light_var.set("N/A")
        self.object_var.set("No Objects Detected")

    def receive_data(self):
        while not self.stop_thread and self.is_connected:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    # Read data from serial port
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    if data:
                        self.parse_sensor_data(data)
                time.sleep(0.01)
            except Exception as e:
                if not self.stop_thread:
                    print(f"Error receiving data: {e}")
                    self.disconnect_serial()
                break

    def parse_sensor_data(self, data):
        try:
            # Example format: "TEMP:25.5,LIGHT:850,OBJECT:0"
            parts = data.split(',')
            sensor_data = {}
            for part in parts:
                if ':' in part:
                    key, value = part.split(':')
                    sensor_data[key.strip()] = value.strip()
            
            # Update the GUI with received data
            if 'TEMP' in sensor_data:
                self.temp_var.set(f"{sensor_data['TEMP']} °C")
                temp_value = sensor_data['TEMP']
            else:
                temp_value = 'N/A'
            
            if 'LIGHT' in sensor_data:
                self.light_var.set(f"{sensor_data['LIGHT']}")
                light_value = sensor_data['LIGHT']
            else:
                light_value = 'N/A'
            
            if 'OBJECT' in sensor_data:
                if sensor_data['OBJECT'] == '1':
                    self.object_var.set("Object Detected!")
                    object_detected = True
                else:
                    self.object_var.set("No Objects Detected")
                    object_detected = False
            else:
                object_detected = False

            # Save the data point
            if all([temp_value != 'N/A', light_value != 'N/A']):
                self.save_data_point(temp_value, light_value, object_detected)
                    
        except Exception as e:
            print(f"Error parsing sensor data: {e}")

    def save_data_point(self, temp, light, object_detected):
        new_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': float(temp) if temp != 'N/A' else None,
            'light_intensity': int(light) if light != 'N/A' else None,
            'object_detected': object_detected
        }
        # Add to DataFrame
        self.historical_data = pd.concat([
            self.historical_data, 
            pd.DataFrame([new_data])
        ], ignore_index=True)
        
        # Save to CSV
        self.historical_data.to_csv(self.data_file, index=False)
        print(f"Saved data point: {new_data}")

    def view_historical_data_table(self, no_records):
        if no_records == "Select Number of Records":
            no_records = "50"

        no_records = int(no_records)

        # Display historical data in a table format
        if self.historical_data.empty:
            messagebox.showinfo("Historical Data", "No historical data available yet.")
            return
        
        # Create a new window
        table_window = tk.Toplevel(self.root)
        table_window.title("Historical Data Table")
        table_window.geometry("1000x400")
        
        # Create Treeview
        tree = ttk.Treeview(table_window, columns=('timestamp', 'temperature', 'light_intensity', 'object_detected'), show='headings')
        
        # Define headings
        tree.heading('timestamp', text='Timestamp')
        tree.heading('temperature', text='Temperature (°C)')
        tree.heading('light_intensity', text='Light Intensity')
        tree.heading('object_detected', text='Object Detected')
        
        # Define column widths
        tree.column('timestamp', width=200)
        tree.column('temperature', width=150)
        tree.column('light_intensity', width=150)
        tree.column('object_detected', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert data 
        recent_data = self.historical_data.tail(no_records)
        for _, row in recent_data.iterrows():
            tree.insert('', tk.END, values=(
                row['timestamp'],
                row['temperature'],
                row['light_intensity'],
                'Yes' if row['object_detected'] else 'No'
            ))

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

        # MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        delta = librosa.feature.delta(mfccs)
        delta2 = librosa.feature.delta(mfccs, order=2)
        features = np.vstack([mfccs, delta, delta2])  # shape (39, frames)

        # Mean + Std 
        mfccs_mean = np.mean(features.T, axis=0)
        mfccs_std = np.std(features.T, axis=0)

        # Extra features: RMS, ZCR, Pitch 
        rms = np.mean(librosa.feature.rms(y=audio_data))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y=audio_data))
        pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
        pitch_mean = np.mean(pitch[pitch > 0]) if np.any(pitch > 0) else 0

        # Final feature vector (81 features) 
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
            self.serial_conn.write(b"on")
            messagebox.showinfo("Voice Command", "System Turned ON by voice!")
        # OFF condition        
        else:  
            self.on_off_var.set("OFF")
            self.current_state = "OFF"
            self.serial_conn.write(b"off")
            time.sleep(0.1)
            messagebox.showinfo("Voice Command", "System Turned OFF by voice!")
            if self.is_connected:
                self.disconnect_serial()
        

Ground_Station()