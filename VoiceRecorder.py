from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import numpy as np
import time
class VoiceRecorderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Recorder")
        
        # Load background image
        self.bg_image = Image.open("background_image.jpeg")
        self.bg_image = self.bg_image.resize((500, 400), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.background_label = tk.Label(master, image=self.bg_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Canvas for waveform visualization
        self.canvas = tk.Canvas(master, width=400, height=100)
        self.canvas.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        # Frame for recordings list
        self.recordings_frame = tk.Frame(master)
        self.recordings_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        # Initialize recordings list
        self.recordings = []
        
        # Buttons
        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.start_button.place(relx=0.3, rely=0.8, anchor=tk.CENTER)
        
        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording)
        self.stop_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
        self.stop_button['state'] = 'disabled'
        
        self.download_button = tk.Button(master, text="Download", command=self.download_recording)
        self.download_button.place(relx=0.7, rely=0.8, anchor=tk.CENTER)
        self.download_button['state'] = 'disabled'
        
        # Label for recording time
        self.time_label = tk.Label(master, text="00:00")
        self.time_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        
        # Variables
        self.recording = False
        self.audio_file_name = "recorded_audio.wav"
        self.start_time = None

    def start_recording(self):
        self.recording = True
        self.start_button['state'] = 'disabled'
        self.stop_button['state'] = 'normal'
        self.download_button['state'] = 'disabled'
        self.start_time = time.time()  # Record the start time
        threading.Thread(target=self.record_audio).start()
        self.update_timer()  # Start updating the timer

    def stop_recording(self):
        self.recording = False
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'
        self.download_button['state'] = 'normal'
        self.visualize_waveform()
        self.add_recording_to_list()
        self.time_label.config(text="00:00")  # Reset the timer label

    def update_timer(self):
        if self.recording:
            current_time = time.time() - self.start_time
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=time_str)
            self.master.after(1000, self.update_timer)  # Update every second

    def record_audio(self, channels=1, rate=44100, chunk=1024, format=pyaudio.paInt16):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=format, channels=channels,
                            rate=rate, input=True,
                            frames_per_buffer=chunk)
        
        frames = []
        while self.recording:
            data = stream.read(chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        with wave.open(self.audio_file_name, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        
    def download_recording(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            import shutil
            shutil.copy(self.audio_file_name, file_path)
        
    def visualize_waveform(self):
        wf = wave.open(self.audio_file_name, 'rb')
        signal = wf.readframes(-1)
        signal = np.frombuffer(signal, 'int16')
        plt.plot(signal)
        plt.axis('off')
        plt.savefig("waveform.png")
        plt.close()
        
        waveform_image = Image.open("waveform.png")
        waveform_image = waveform_image.resize((400, 100), Image.LANCZOS)
        waveform_photo = ImageTk.PhotoImage(waveform_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=waveform_photo)
        self.canvas.image = waveform_photo
    
    def add_recording_to_list(self):
        recording_frame = tk.Frame(self.recordings_frame)
        recording_frame.pack(anchor=tk.W)
        
        recording_label = tk.Label(recording_frame, text=f"Recording {len(self.recordings) + 1}")
        recording_label.pack(side=tk.LEFT)
        
        play_button = tk.Button(recording_frame, text="Play", command=lambda idx=len(self.recordings): self.play_recording(idx))
        play_button.pack(side=tk.LEFT)
        
        self.recordings.append(self.audio_file_name)

    def play_recording(self, idx):
        if idx < len(self.recordings):
            audio_file = self.recordings[idx]
            sound = AudioSegment.from_wav(audio_file)
            play(sound)

def main():
    root = tk.Tk()
    root.geometry("500x400")
    app = VoiceRecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()