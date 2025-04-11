# takes user voice as input from mic 
# passes it to voice processor
# takes user voice as input from mic 
# passes it to voice processor

import threading
import datetime
import os
import pvporcupine
import pyaudio
import struct
import wave
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables from .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env.local'))
load_dotenv(dotenv_path)

class VoiceAssistant:
    def list_input_devices():
        pa = pyaudio.PyAudio()
        print("\nAvailable audio input devices:\n")
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"ID {i}: {info['name']}")
        pa.terminate()

    def __init__(self, hotword="jarvis", record_duration=5):
        self.hotword = hotword
        self.record_duration = record_duration
        self.recognizer = sr.Recognizer()
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")

    # Debug print to verify key loading
        # print(f"[DEBUG] Loaded Picovoice Access Key: {access_key}")

        if not access_key:
            raise ValueError("⚠️ Missing Picovoice access key. Set PICOVOICE_ACCESS_KEY in your .env file.")

        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=[self.hotword]
        )

        self.hotword = hotword
        self.record_duration = record_duration
        self.recognizer = sr.Recognizer()
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")

        if not access_key:
            raise ValueError("⚠️ Missing Picovoice access key. Set PICOVOICE_ACCESS_KEY in your .env file.")

        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=[self.hotword]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )
    
    def _record_audio(self):
        print("[🎙️] Recording voice...")
        RATE = 16000
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []

        for _ in range(int(RATE / CHUNK * self.record_duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("recordings", exist_ok=True)
        filename = f"recordings/voice_{timestamp}.wav"

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        return filename

    def _recognize_and_execute(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                print(f"[🗣️] You said: {text}")
                # 🔁 Add execution logic here
                # self.execute_command(text)
        except sr.UnknownValueError:
            print("[❓] Couldn't understand what you said.")
        except Exception as e:
            print(f"[⚠️] Error in recognition: {e}")

    def _handle_hotword_trigger(self):
        filename = self._record_audio()
        self._recognize_and_execute(filename)

    def start_hotword_listener(self):
        print("🎧 Hotword listener started... Say your hotword to begin.")
        try:
            while True:
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm)

                if result >= 0:
                    print("[🔊] Hotword detected!")
                    t = threading.Thread(target=self._handle_hotword_trigger)
                    t.start()

        except KeyboardInterrupt:
            print("\n[🛑] Hotword listener stopped.")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
            self.porcupine.delete()
