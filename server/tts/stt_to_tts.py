import os
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
from faster_whisper import WhisperModel
from TTS.api import TTS
import torch

# === ENV FIX ===
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Prevent OpenMP crash

# === SETTINGS ===
model_size = "medium"
device = "cuda"
compute_type = "int8"
sample_rate = 16000
output_dir = "G:/final/tts"
os.makedirs(output_dir, exist_ok=True)

# === INITIALIZE WHISPER MODEL ===
model = WhisperModel(model_size, device=device, compute_type=compute_type)

# === INITIALIZE TTS MODEL ===
if torch.cuda.is_available():
    print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA is not available. Falling back to CPU.")

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=True)

# === FIND AUDIORELAY INPUT DEVICE ===
def find_audiorelay_input():
    for i, device in enumerate(sd.query_devices()):
        name = device['name'].lower()
        if "audiorelay" in name and device['max_input_channels'] > 0:
            print(f"Using input device: {device['name']} (index {i})")
            return i
    raise RuntimeError("No AudioRelay input device found.")

try:
    input_device_index = find_audiorelay_input()
except RuntimeError as e:
    print(e)
    exit(1)

# === VARIABLES ===
recording = False
audio_data = []

# === AUDIO CALLBACK ===
def audio_callback(indata, frames, time_info, status):
    if recording:
        audio_data.append(indata.copy())

# === TRANSCRIPTION FUNCTION ===
def transcribe_audio(file_path):
    print("Transcribing...")
    start_time = time.time()
    segments, info = model.transcribe(file_path, beam_size=5)
    end_time = time.time()

    print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")
    full_text = ""
    for segment in segments:
        print(segment.text)
        full_text += segment.text.strip() + " "
    print(f"Time taken for transcription: {end_time - start_time:.2f} seconds")
    return full_text.strip()

# === TEXT-TO-SPEECH FUNCTION ===
def synthesize_speech(text, output_filename="response.wav"):
    if not text:
        print("No text to synthesize.")
        return
    output_path = os.path.join(output_dir, output_filename)
    print(f"Synthesizing speech: '{text}'")
    tts.tts_to_file(text=text, file_path=output_path, split_sentences=False)
    print(f"Synthesized speech saved to: {output_path}")

# === KEYBOARD HANDLERS ===
def on_press(key):
    global recording, audio_data
    if key == keyboard.Key.space and not recording:
        print("Recording... (hold SPACE)")
        audio_data = []
        recording = True
        stream.start()

def on_release(key):
    global recording
    if key == keyboard.Key.space and recording:
        print("Stopped recording.")
        recording = False
        stream.stop()

        # Save recorded audio
        recorded_audio = np.concatenate(audio_data)
        recorded_audio = np.int16(recorded_audio * 32767)
        filename = "mic_input.wav"
        wav.write(filename, sample_rate, recorded_audio)

        # Transcribe
        transcribed_text = transcribe_audio(filename)

        # Synthesize
        synthesize_speech(transcribed_text, output_filename="response.wav")

        # Clean up
        os.remove(filename)

    if key == keyboard.Key.esc:
        print("Exiting...")
        return False

# === START AUDIO STREAM ===
stream = sd.InputStream(
    samplerate=sample_rate,
    channels=1,
    callback=audio_callback,
    device=input_device_index
)

# === START LISTENING LOOP ===
print("🎙️ Press and hold SPACE to record. Release to transcribe & synthesize. Press ESC to exit.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
