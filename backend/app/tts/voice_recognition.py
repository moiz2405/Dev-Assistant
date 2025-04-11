import threading
import datetime
import os
import time
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

    def cleanup_old_recordings(self, folder="recordings", max_age_minutes=10):
        now = time.time()
        max_age_seconds = max_age_minutes * 60
        if not os.path.exists(folder):
            return
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if filename.endswith(".wav"):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        print(f"[🧹] Deleted old recording: {filename}")
                    except Exception as e:
                        print(f"[⚠️] Could not delete {filename}: {e}")

    def __init__(self, hotword="jarvis", record_duration=5, cooldown_seconds=2):
        self.hotword = hotword
        self.record_duration = record_duration
        self.cooldown_seconds = cooldown_seconds
        self.recognizer = sr.Recognizer()
        self.listening_lock = threading.Lock()

        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not access_key:
            raise ValueError("⚠️ Missing Picovoice access key. Set PICOVOICE_ACCESS_KEY in your .env file.")

        self.porcupine = pvporcupine.create(access_key=access_key, keywords=[self.hotword])
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
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []

        for _ in range(int(RATE / CHUNK * self.record_duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                print(f"[⚠️] Error while recording: {e}")

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
                # TODO: Add command execution here
        except sr.UnknownValueError:
            print("[❓] Couldn't understand what you said.")
        except Exception as e:
            print(f"[⚠️] Error in recognition: {e}")

    def _beep(self):
        print('\a', end='', flush=True)

    def _handle_hotword_trigger(self):
        def inner():
            with self.listening_lock:
                self._beep()
                filename = self._record_audio()
                try:
                    self._recognize_and_execute(filename)
                finally:
                    self.cleanup_old_recordings()
                    print("[✅] Ready for next command...")
    
        threading.Thread(target=inner, daemon=True).start()


    def start_hotword_listener(self):
        print("🎧 Hotword listener started... Say your hotword to begin.")
        last_trigger_time = 0
        try:
            while True:
                try:
                    pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    result = self.porcupine.process(pcm)
                except Exception as e:
                    print(f"[⚠️] Error reading audio stream: {e}")
                    continue

                if result >= 0:
                    current_time = time.time()
                    if current_time - last_trigger_time >= self.cooldown_seconds and not self.listening_lock.locked():
                        print("[🔊] Hotword detected!")
                        last_trigger_time = current_time
                        threading.Thread(target=self._handle_hotword_trigger, daemon=True).start()

        except KeyboardInterrupt:
            print("\n[🛑] Hotword listener stopped.")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
            self.porcupine.delete()
