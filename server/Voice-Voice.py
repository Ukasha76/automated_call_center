import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
from faster_whisper import WhisperModel
import asyncio
import torchaudio
import os
from router_main import HospitalRouter
from tts.main import text_to_speech

# === TEXT SPLITTER (not used, but retained if needed) ===
def split_text_optimized(text, max_chars=150):
    sentences = []
    current_sentence = ""
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    for paragraph in paragraphs:
        sentences_in_para = [s.strip() for s in paragraph.split('.') if s.strip()]
        for sentence in sentences_in_para:
            if len(current_sentence) + len(sentence) < max_chars:
                current_sentence += " " + sentence + "."
            else:
                if current_sentence:
                    sentences.append(current_sentence.strip())
                current_sentence = sentence + "."
    if current_sentence:
        sentences.append(current_sentence.strip())
    return sentences

# === AUDIO PLAYBACK (if you need it) ===
def play_audio(file_path):
    try:
        audio, sample_rate = torchaudio.load(file_path)
        audio_np = audio.numpy()
        if audio_np.ndim > 1:
            audio_np = np.mean(audio_np, axis=0)
        print("\nPlaying audio... (Press Ctrl+C to stop)")
        sd.play(audio_np, sample_rate)
        sd.wait()
        print("Playback completed.")
    except Exception as e:
        print(f"\nCouldn't play audio: {str(e)}")

def voice(text: str) -> float:
    return text_to_speech(text)


# === SETTINGS ===
model_size = "large"
device = "cuda"
compute_type = "int8"
sample_rate = 16000

# === GLOBALS ===
recording = False
audio_data = []
stream = None
router = None
loop = None
total_start_time = 0

# === INITIALIZE WHISPER MODEL ===
model = WhisperModel(model_size, device=device, compute_type=compute_type)

# === FIND INPUT DEVICE ===
def find_input_device():
    for i, device in enumerate(sd.query_devices()):
        name = device['name'].lower()
        if "audiorelay" in name and device['max_input_channels'] > 0:
            print(f"Using input device: {device['name']} (index {i})")
            return i
    raise RuntimeError("No AudioRelay input device found.")

try:
    input_device_index = find_input_device()
except RuntimeError as e:
    print(e)
    exit(1)

# === AUDIO CALLBACK ===
def audio_callback(indata, frames, time, status):
    if recording:
        audio_data.append(indata.copy())

# === PROCESS TRANSCRIPTION ===
async def process_transcription(text: str, stt_duration: float):
    global router, total_start_time
    if not router:
        router = await HospitalRouter.create()
    
    try:
        # Text-to-text
        text_to_text_start = time.time()
        response = await router.process_query(text)
        text_to_text_end = time.time()
        text_to_text_duration = text_to_text_end - text_to_text_start

        # TTS
        tts_start = time.time()
        first_chunk_time = voice(response.get('response', 'Issue in getting response'))
        tts_end = time.time()
        tts_duration = tts_end - tts_start

        # Final output
        print(f"\nAgent: {response['response']}")
        total_duration = time.time() - total_start_time
        print("\n=== Timing Summary ===")
        print(f"STT Duration         : {stt_duration:.2f} seconds")
        print(f"Text-to-Text Duration: {text_to_text_duration:.2f} seconds")
        print(f"TTS Duration         : {tts_duration:.2f} seconds")
        print(f"🗣️ First Chunk Time    : {first_chunk_time:.2f} seconds")
        print(f"Total Interaction    : {total_duration:.2f} seconds")
        print("======================\n")


    except Exception as e:
        print(f"Error processing query: {str(e)}")

# === TRANSCRIBE AUDIO ===
async def transcribe_audio(file_path):
    print("Transcribing...")
    stt_start = time.time()
    segments, info = model.transcribe(file_path, beam_size=5, language="en")
    stt_end = time.time()

    stt_duration = stt_end - stt_start
    full_text = " ".join([segment.text for segment in segments])

    print(f"\nTranscription: {full_text}")
    print(f"Time taken in STT: {stt_duration:.2f} seconds")

    if full_text.strip():
        await process_transcription(full_text, stt_duration)
    
    # Optionally clean up
    os.remove(file_path)

# === KEYBOARD HANDLERS ===
def on_press(key):
    global recording, audio_data

    if key == keyboard.Key.space and not recording:
        print("\nRecording... (hold SPACE)")
        audio_data = []
        recording = True
        stream.start()

def on_release(key):
    global recording, loop, total_start_time

    if key == keyboard.Key.space and recording:
        total_start_time = time.time()
        print("Stopped recording.")
        recording = False
        stream.stop()

        if audio_data:
            recorded_audio = np.concatenate(audio_data)
            recorded_audio = np.clip(recorded_audio, -1, 1)
            recorded_audio = np.int16(recorded_audio * 32767)
            filename = "temp_audio.wav"
            wav.write(filename, sample_rate, recorded_audio)

            if loop:
                asyncio.run_coroutine_threadsafe(transcribe_audio(filename), loop)

    if key == keyboard.Key.esc:
        print("\nExiting...")
        if loop:
            asyncio.run_coroutine_threadsafe(shutdown(), loop)
        return False

# === MAIN ===
async def main():
    global stream, router, loop

    loop = asyncio.get_running_loop()
    router = await HospitalRouter.create()
    print("HospitalRouter initialized")

    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        callback=audio_callback,
        device=input_device_index
    )

    print("\nPress and hold SPACE to record. Release to transcribe. Press ESC to exit.")

    def start_listener():
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    await loop.run_in_executor(None, start_listener)

# === SHUTDOWN CLEANUP ===
async def shutdown():
    global router, stream
    if router:
        await router._cleanup_sessions()
    if stream:
        stream.close()
    print("\nCleanup complete")

# === ENTRY POINT ===
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        asyncio.run(shutdown())
