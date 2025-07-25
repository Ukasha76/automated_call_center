import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
from faster_whisper import WhisperModel
import asyncio
from datetime import datetime
# from router_main import HospitalRouter
import torch
from TTS.api import TTS
import os
import time
import torchaudio
import sounddevice as sd
import numpy as np

from tts.tts_with_clone import TextToSpeech


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

def speak_text(text: str):
    tts = TextToSpeech()
    tts.speak(text)
#     print('hi')

