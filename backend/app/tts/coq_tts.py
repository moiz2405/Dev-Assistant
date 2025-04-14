from TTS.api import TTS

# Load a pre-trained model (English, high quality)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

# Synthesize speech to a file
tts.tts_to_file(text="Hello! This is Coqui TTS speaking.", file_path="output.wav")
