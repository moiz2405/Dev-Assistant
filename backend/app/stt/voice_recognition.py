import threading
import datetime
import os
import time
import pvporcupine
import pyaudio
import struct
import wave
import speech_recognition as sr
import logging
import sys
import audioop
from dotenv import load_dotenv


# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env.local'))
load_dotenv(dotenv_path)


class VoiceAssistant:
    @staticmethod
    def list_input_devices():
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"ID {i}: {info['name']}")
        pa.terminate()

    def cleanup_old_recordings(self, folder="recordings", max_age_minutes=1):
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
                        print(f"Deleted old recording: {filename}")
                    except Exception as e:
                        print(f"Could not delete {filename}: {e}")

    def __init__(self, hotword="vision", record_duration=6, cooldown_seconds=2, on_recognized=None):
        self.hotword = hotword
        self.record_duration = record_duration
        self.cooldown_seconds = cooldown_seconds
        self.recognizer = sr.Recognizer()
        self.listening_lock = threading.Lock()
        self.on_recognized = on_recognized or self.default_command_handler

        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not access_key:
            raise ValueError("Missing Picovoice access key. Set PICOVOICE_ACCESS_KEY in your .env file.")

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Dynamically get the absolute path of the keyword file inside 'vision_wake_word' directory
        # keyword_path = os.path.join(os.path.dirname(__file__), "vision_wake_word", "vision_en_linux_v3_0_0.ppn")
        # keyword_path = os.path.join(os.path.dirname(__file__), "../../vision_wake_word/vision_en_linux_v3_0_0.ppn")
        keyword_path = "/mnt/d/projects/MYPROJECTS/Dev-Assistant/vision_wake_word/vision_en_linux_v3_0_0.ppn"
        print(keyword_path)
        if not os.path.exists(keyword_path):
            raise FileNotFoundError(f"Keyword file not found at {keyword_path}")

        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )

    def _beep(self):
        print('\a', end='', flush=True)

    def _record_audio_dynamic(self):
        print("Listening for command...")
        os.makedirs("recordings", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/voice_{timestamp}.wav"

        RATE = 16000
        CHUNK = 1024
        SILENCE_THRESHOLD = 100  # Adjust based on testing
        MAX_SILENCE_CHUNKS = int(1.5 * RATE / CHUNK)  # 1.2 sec of silence
        MAX_RECORD_SECONDS = 10

        stream = self.pa.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        print("Start speaking now...")
        frames = []
        silent_chunks = 0
        speaking_started = False
        start_time = time.time()

        while True:
            data = stream.read(CHUNK)
            rms = audioop.rms(data, 2)  # Root mean square to detect volume
            frames.append(data)

            if rms > SILENCE_THRESHOLD:
                silent_chunks = 0
                speaking_started = True
            else:
                if speaking_started:
                    silent_chunks += 1

            if silent_chunks > MAX_SILENCE_CHUNKS:
                print("Silence detected, stopping recording.")
                break

            if time.time() - start_time > MAX_RECORD_SECONDS:
                print("Max recording time reached.")
                break

        stream.stop_stream()
        stream.close()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        return filename

    def _recognize_and_execute(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                print(f"You said: {text}")

                if self.on_recognized:
                    self.on_recognized(text)
        except sr.UnknownValueError:
            print("Couldn't understand what you said.")
        except Exception as e:
            print(f"Recognition error: {e}")

    def _handle_hotword_trigger(self):
        def inner():
            with self.listening_lock:
                self._beep()
                filename = self._record_audio_dynamic()
                if filename:
                    try:
                        self._recognize_and_execute(filename)
                    finally:
                        self.cleanup_old_recordings()
                print("Ready for next command...")

        threading.Thread(target=inner, daemon=True).start()

    def _restart_stream(self):
        print("Restarting audio stream...")
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )
        except Exception as e:
            print(f"Failed to restart stream: {e}")

    def start_hotword_listener(self):
        print("Hotword listener started...")
        last_trigger_time = 0
        
        try:
            while True:
                try:
                    pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    result = self.porcupine.process(pcm)
                except Exception as e:
                    self._restart_stream()
                    continue

                if result >= 0:
                    current_time = time.time()
                    if current_time - last_trigger_time >= self.cooldown_seconds and not self.listening_lock.locked():
                        print("Hotword detected!")
                        last_trigger_time = current_time
                        self._handle_hotword_trigger()

        except KeyboardInterrupt:
            print("Voice assistant stopped.")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
            self.porcupine.delete()

    @staticmethod
    def default_command_handler(command):
        if "time" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            print(f"The current time is {now}.")
        else:
            print(f"Command received: {command}")
