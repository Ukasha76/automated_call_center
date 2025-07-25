import torch
# import torchaudio as ta
# from chatterbox.tts import ChatterboxTTS

# Check if CUDA (GPU) is available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")



# model = ChatterboxTTS.from_pretrained(device="cuda")

# text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
# wav = model.generate(text)
# ta.save("test-1.wav", wav, model.sr)

# import torch
# from TTS.api import TTS
# import os
# import time
# import torchaudio
# import sounddevice as sd
# import numpy as np

# def split_text_optimized(text, max_chars=150):
#     sentences = []
#     current_sentence = ""
    
#     # First split by paragraphs
#     paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
#     for paragraph in paragraphs:
#         # Then split by sentences within paragraphs
#         sentences_in_para = [s.strip() for s in paragraph.split('.') if s.strip()]
        
#         for sentence in sentences_in_para:
#             if len(current_sentence) + len(sentence) < max_chars:
#                 current_sentence += " " + sentence + "."
#             else:
#                 if current_sentence:
#                     sentences.append(current_sentence.strip())
#                 current_sentence = sentence + "."
    
#     if current_sentence:
#         sentences.append(current_sentence.strip())
    
#     return sentences

# def play_audio(file_path):
#     try:
#         # Load audio file using torchaudio
#         audio, sample_rate = torchaudio.load(file_path)
        
#         # Convert to numpy array and ensure it's mono
#         audio_np = audio.numpy()
#         if audio_np.ndim > 1:
#             audio_np = np.mean(audio_np, axis=0)  # Convert to mono if stereo
        
#         print("\nPlaying audio... (Press Ctrl+C to stop)")
#         sd.play(audio_np, sample_rate)
#         sd.wait()  # This will block until playback is finished
#         print("Playback completed.")
#     except Exception as e:
#         print(f"\nCouldn't play audio: {str(e)}")

# def process_text_chunks(text, output_name, tts_model, device):
#     print(f"\nProcessing {output_name}...")
    
#     # Output path
#     current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
#     output_path = os.path.join(current_dir, f"{output_name}.wav")
    
#     text_chunks = split_text_optimized(text)
#     print(f"Split into {len(text_chunks)} optimal chunks")
    
#     # Process chunks with detailed tracking
#     wav_chunks = []
#     start_time = time.time()
#     processed_chars = 0
#     total_chars = len(text)
    
#     for i, chunk in enumerate(text_chunks, 1):
#         chunk_start = time.time()
#         processed_chars += len(chunk)
        
#         # Generate audio for this chunk
#         chunk_path = f"temp_chunk_{i}.wav"


#         tts_model.tts_to_file(text=chunk, speaker_wav="audio.wav" , file_path=chunk_path)
        
#         # Load and process the chunk
#         audio, sample_rate = torchaudio.load(chunk_path)
#         wav_chunks.append(audio)
#         os.remove(chunk_path)
        
#         # Progress tracking
#         chunk_time = time.time() - chunk_start
#         progress_percent = (processed_chars / total_chars) * 100
        
#         if i == 1:
#             first_chunk_time = time.time() - start_time
#             print(f"\nTime to first chunk: {first_chunk_time:.2f}s")
        
#         print(f"Chunk {i}/{len(text_chunks)} | {len(chunk.split())} words | "
#               f"Progress: {progress_percent:.1f}% | Time: {chunk_time:.2f}s")
    
#     # Combine all chunks
#     if wav_chunks:
#         full_audio = torch.cat(wav_chunks, dim=1)
#         torchaudio.save(output_path, full_audio, sample_rate)
        
#         total_time = time.time() - start_time
#         audio_length = full_audio.shape[1] / sample_rate
        
#         print(f"\n{'='*40}")
#         print(f"Total words processed: {len(text.split())}")
#         print(f"Total processing time: {total_time:.2f}s")
#         print(f"Audio duration: {audio_length:.2f}s")
#         print(f"Real-time factor: {total_time/audio_length:.2f}")
#         print(f"Output saved to: {output_path}")
#         print(f"{'='*40}")
        
#         # Play the result
#         play_audio(output_path)
#     else:
#         print("No audio was generated")

# def main():
#     # Select device (GPU or CPU) and print status
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"Using device: {device.upper()}")

#     # Initialize TTS modeltts_models/en/sam/fast_pitch
#     tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch").to(device)

#     # Text to synthesize
#     full_text = """
# I can help with that!

# Hi there. To be admitted to Osaka University Hospital, you ll need to follow these steps according to the Hospital Admission Process and Admission Guidelines and Procedures:

# Get the Date
# Your doctor will inform you of the date you need to be admitted. If the admission is required after an outpatient visit, your doctor will register the admission, and the clinical section will contact you with the specific time.
# Gather your documents.

# Ensure you have your patient registration card, personal seal, and admission application form ready. You can find more details about required materials in the Hospital Admission Process.

# Arrive at Inpatients Reception
# On the day of admission, go to the Inpatients Reception with all your documents.

# Complete Admission
# You or a representative will need to complete the admission procedure before going to your ward.



# """

#     # Count total words and split into halves
#     all_words = full_text.split()
#     total_words = len(all_words)
#     halfway_point = total_words // 2
#     first_half_text = ' '.join(all_words[:halfway_point])
#     second_half_text = ' '.join(all_words[halfway_point:])

#     print(f"\nTotal words: {total_words}")
#     print(f"First half: {halfway_point} words")
#     print(f"Second half: {total_words - halfway_point} words")

#     # Process and play first half
#     process_text_chunks(first_half_text, "first_half_output", tts, device)

#     # Process and play second half
#     process_text_chunks(second_half_text, "second_half_output", tts, device)

#     print("\nAll processing complete!")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\nPlayback interrupted by user")
#     except Exception as e:
#         print(f"\nAn error occurred: {str(e)


import torch
from TTS.api import TTS
import os
import time
import torchaudio
import sounddevice as sd
import numpy as np
# List available 🐸TTS models
print(TTS().list_models())
# def split_text_optimized(text, max_chars=150):
#     sentences = []
#     current_sentence = ""
    
#     # First split by paragraphs
#     paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
#     for paragraph in paragraphs:
#         # Then split by sentences within paragraphs
#         sentences_in_para = [s.strip() for s in paragraph.split('.') if s.strip()]
        
#         for sentence in sentences_in_para:
#             if len(current_sentence) + len(sentence) < max_chars:
#                 current_sentence += " " + sentence + "."
#             else:
#                 if current_sentence:
#                     sentences.append(current_sentence.strip())
#                 current_sentence = sentence + "."
    
#     if current_sentence:
#         sentences.append(current_sentence.strip())
    
#     return sentences
def split_text_optimized(text, max_chars=150, min_chars=5):
    sentences = []
    current_sentence = ""
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    for paragraph in paragraphs:
        sentences_in_para = [s.strip() for s in paragraph.split('.') if s.strip()]
        
        for sentence in sentences_in_para:
            if len(current_sentence) + len(sentence) < max_chars:
                current_sentence += " " + sentence + "."
            else:
                if current_sentence and len(current_sentence) >= min_chars:
                    sentences.append(current_sentence.strip())
                current_sentence = sentence + "."
    
    if current_sentence and len(current_sentence) >= min_chars:
        sentences.append(current_sentence.strip())
    
    # Handle remaining very short chunks
    if not sentences and text.strip():
        sentences.append(text[:max_chars])
    
    return sentences

def play_audio(file_path):
    try:
        # Load audio file using torchaudio
        audio, sample_rate = torchaudio.load(file_path)
        
        # Convert to numpy array and ensure it's mono
        audio_np = audio.numpy()
        if audio_np.ndim > 1:
            audio_np = np.mean(audio_np, axis=0)  # Convert to mono if stereo
        
        print("\nPlaying audio... (Press Ctrl+C to stop)")
        sd.play(audio_np, sample_rate)
        sd.wait()  # This will block until playback is finished
        print("Playback completed.")
    except Exception as e:
        print(f"\nCouldn't play audio: {str(e)}")

# def process_text_chunks(text, output_name, tts_model, device):
#     # print(f"\nProcessing {output_name}...")
    
#     # # Output path
#     # current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
#     # output_path = os.path.join(current_dir, f"{output_name}.wav")
    
#     # text_chunks = split_text_optimized(text)
#     # print(f"Split into {len(text_chunks)} optimal chunks")
    
#     # # Process chunks with detailed tracking
#     wav_chunks = []
#     start_time = time.time()
#     processed_chars = 0
#     total_chars = len(text)
    
#     # for i, chunk in enumerate(text_chunks, 1):
#     #     chunk_start = time.time()
#     #     processed_chars += len(chunk)
        
#     #     # Generate audio for this chunk
#     #     chunk_path = f"temp_chunk_{i}.wav"
#     #     tts_model.tts_to_file(text=chunk, speaker_wav="audio.wav", file_path=chunk_path)
        
#     #     # Load and process the chunk
#     #     audio, sample_rate = torchaudio.load(chunk_path)
#     #     wav_chunks.append(audio)
#     #     os.remove(chunk_path)
        
#     #     # Progress tracking
#     #     chunk_time = time.time() - chunk_start
#     #     progress_percent = (processed_chars / total_chars) * 100
        
#     #     if i == 1:
#     #         first_chunk_time = time.time() - start_time
#     #         print(f"\nTime to first chunk: {first_chunk_time:.2f}s")
        
#     #     print(f"Chunk {i}/{len(text_chunks)} | {len(chunk.split())} words | "
#     #           f"Progress: {progress_percent:.1f}% | Time: {chunk_time:.2f}s")
#     print(f"\nProcessing {output_name}...")
    
#     # Output path
#     current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
#     output_path = os.path.join(current_dir, f"{output_name}.wav")
    
#     # Modified text splitting with minimum length enforcement
#     text_chunks = [chunk for chunk in split_text_optimized(text) if len(chunk.strip()) > 3]
#     if not text_chunks:  # Handle empty input case
#         text_chunks = [text[:150]] if text else ["Empty input"]
    
#     print(f"Split into {len(text_chunks)} chunks (after filtering)")
    
#     # Process chunks with dimension handling
#     wav_chunks = []
#     sample_rate = None
    
#     for i, chunk in enumerate(text_chunks, 1):
#         try:
#             chunk_path = f"temp_chunk_{i}.wav"
            
#             # Ensure chunk has minimum meaningful content
#             processed_chunk = chunk if len(chunk.split()) > 1 else f"{chunk} (pause)"
            
#             tts_model.tts_to_file(
#                 text=processed_chunk,
#                 speaker_wav="audio.wav",
#                 file_path=chunk_path
#             )
            
#             # Load with explicit channel dimension handling
#             audio, sr = torchaudio.load(chunk_path)
#             if sample_rate is None:
#                 sample_rate = sr
            
#             # Ensure proper tensor dimensions [channels, time]
#             if audio.dim() == 1:
#                 audio = audio.unsqueeze(0)
#             elif audio.dim() == 2 and audio.size(0) > audio.size(1):
#                 audio = audio.transpose(0, 1)
                
#             wav_chunks.append(audio)
            
#         except Exception as e:
#             print(f"Error processing chunk {i}: {str(e)}")
#         finally:
#             if os.path.exists(chunk_path):
#                 os.remove(chunk_path)   
#     # Combine all chunks
#     if wav_chunks:
#         full_audio = torch.cat(wav_chunks, dim=1)
#         torchaudio.save(output_path, full_audio, sample_rate)
        
#         total_time = time.time() - start_time
#         audio_length = full_audio.shape[1] / sample_rate
        
#         print(f"\n{'='*40}")
#         print(f"Total words processed: {len(text.split())}")
#         print(f"Total processing time: {total_time:.2f}s")
#         print(f"Audio duration: {audio_length:.2f}s")
#         print(f"Real-time factor: {total_time/audio_length:.2f}")
#         print(f"Output saved to: {output_path}")
#         print(f"{'='*40}")
        
#         # Play the result
#         play_audio(output_path)
#     else:
# #         print("No audio was generated")
# def process_text_chunks(text, output_name, tts_model, device):
#     print(f"\nProcessing {output_name}...")
    
#     # Output path
#     current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
#     output_path = os.path.join(current_dir, f"{output_name}.wav")
    
#     # Get chunks with minimum length enforcement
#     text_chunks = split_text_optimized(text)
#     print(f"Split into {len(text_chunks)} chunks")
    
#     # Process chunks
#     wav_chunks = []
#     sample_rate = None
    
#     for i, chunk in enumerate(text_chunks, 1):
#         try:
#             chunk_path = f"temp_chunk_{i}.wav"
            
#             # Skip empty or punctuation-only chunks
#             if not chunk.strip() or all(c in '.,!?;:' for c in chunk.strip()):
#                 print(f"Skipping invalid chunk: {chunk}")
#                 continue
                
#             tts_model.tts_to_file(
#                 text=chunk,
#                 speaker_wav="audio.wav",
#                 file_path=chunk_path
#             )
            
#             audio, sr = torchaudio.load(chunk_path)
#             if sample_rate is None:
#                 sample_rate = sr
                
#             wav_chunks.append(audio)
            
#         except Exception as e:
#             print(f"Error processing chunk {i} ('{chunk}'): {str(e)}")
#         finally:
#             if os.path.exists(chunk_path):
#                 os.remove(chunk_path)
    
#     # Combine audio if we have valid chunks
#     if wav_chunks:
#         full_audio = torch.cat(wav_chunks, dim=1)
#         torchaudio.save(output_path, full_audio, sample_rate)
#         play_audio(output_path)
#     else:
#         print("No valid audio was generated")
#         # Generate a fallback audio if needed
#         fallback_text = "Please speak again"
#         tts_model.tts_to_file(text=fallback_text, file_path=output_path)
#         play_audio(output_path)
def process_text_chunks(text, output_name, tts_model, device):
    print(f"\nProcessing {output_name}...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
    output_path = os.path.join(current_dir, f"{output_name}.wav")
    
    text_chunks = split_text_optimized(text)
    print(f"Split into {len(text_chunks)} chunks")
    
    wav_chunks = []
    sample_rate = None
    first_chunk_time = None
    start_time = time.time()  # Start timing

    for i, chunk in enumerate(text_chunks, 1):
        try:
            chunk_path = f"temp_chunk_{i}.wav"
            if not chunk.strip() or all(c in '.,!?;:' for c in chunk.strip()):
                print(f"Skipping invalid chunk: {chunk}")
                continue
     
            # Time the first chunk generation
            chunk_start = time.time()
            tts_model.tts_to_file(
                text=chunk,
                speaker_wav="audio.wav",
                file_path=chunk_path,
                # user_phonemes=True
                
            )
            if i == 1:
                first_chunk_time = time.time() - start_time
                print(f"\n⏱️ Time to first audio chunk: {first_chunk_time:.2f} seconds")
            
            audio, sr = torchaudio.load(chunk_path)
            if sample_rate is None:
                sample_rate = sr
            wav_chunks.append(audio)
        except Exception as e:
            print(f"Error processing chunk {i} ('{chunk}'): {str(e)}")
        finally:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

    if wav_chunks:
        full_audio = torch.cat(wav_chunks, dim=1)
        torchaudio.save(output_path, full_audio, sample_rate)
        play_audio(output_path)
    else:
        print("No valid audio was generated")
        fallback_text = "Please speak again"
        tts_model.tts_to_file(text=fallback_text, file_path=output_path)
        play_audio(output_path)

    return first_chunk_time

    # Rest of your existing combination code...

# def text_to_speech(text, output_name="output", speaker_wav="audio.wav"):
#     """
#     Convert text to speech and play it immediately.
    
#     Args:
#         text (str): The text to convert to speech
#         output_name (str): Base name for output file (without extension)
#         speaker_wav (str): Path to reference speaker audio file for voice cloning
#     """
#     try:
#         # Select device (GPU or CPU) and print status
#         device = "cuda" if torch.cuda.is_available() else "cpu"
#         print(f"Using device: {device.upper()}")

#         # Initialize TTS model
#         tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch").to(device)

#         # Count total words and split into halves if too long
#         all_words = text.split()
#         total_words = len(all_words)
        
#         if total_words > 300:  # Split if more than 300 words
#             halfway_point = total_words // 2
#             first_half_text = ' '.join(all_words[:halfway_point])
#             second_half_text = ' '.join(all_words[halfway_point:])

#             print(f"\nTotal words: {total_words}")
#             print(f"First half: {halfway_point} words")
#             print(f"Second half: {total_words - halfway_point} words")

#             # Process and play first half
           
#             process_text_chunks(first_half_text, f"{output_name}_part1", tts, device)
#             # Process and play second half
#             process_text_chunks(second_half_text, f"{output_name}_part2", tts, device)
#         else:
#             process_text_chunks(text, output_name, tts, device)

#         print("\nAll processing complete!")
#         return True
#     except Exception as e:
#         print(f"\nAn error occurred: {str(e)}")
#         return False
from phonemizer import phonemize

def text_to_speech(text, output_name="output", speaker_wav="audio.wav") -> float:


    """
    Convert text to speech and return time to first audio chunk.
    
    Returns:
        float or None: Time in seconds to first audio chunk, or None on error.
    """
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device.upper()}")
 
        # tts = TTS(model_name="tts_models/en/sam/tacotron-DDC").to(device)
        #0.94 male voice robotic , deep 
 
        tts = TTS(model_name="tts_models/en/ljspeech/vits").to(device)
        # 071 s(good , realistic slightly robotic , pronouncistion best))
    

        # tts = TTS(model_name="tts_models/en/jenny/jenny").to(device)
         #1.81 s ( good , realistic with breath sound , pronouncistion best)
 
        # tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph").to(device)
        #0.84 good , slightly robotic , skipping 

        # tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DCA").to(device)
          # #0.76 good robotic punnc good
        # tts = TTS(model_name="tts_models/en/ljspeech/speedy-speech").to(device)
        # #0.15 , fast, robotic 
      

      

        # tts = TTS(model_name="tts_models/en/ljspeech/glow-tts").to(device)
        # 0.23 s (robotic voice , with punc mistakes)
        
        # tts = TTS(model_name="tts_models/en/ljspeech/vits--neon").to(device)
        # (0.78 , punc is good, slightly robotic)

        
        # tts = TTS(
        #     model_name="tts_models/en/ljspeech/fast_pitch",  # TTS model
        # ).to("cuda")


        all_words = text.split()
        total_words = len(all_words)
        
        if total_words > 300:
            halfway_point = total_words // 2
            first_half_text = ' '.join(all_words[:halfway_point])
            second_half_text = ' '.join(all_words[halfway_point:])

            print(f"\nTotal words: {total_words}")
            print(f"First half: {halfway_point} words")
            print(f"Second half: {total_words - halfway_point} words")

            first_chunk_time = process_text_chunks(first_half_text, f"{output_name}_part1", tts, device)
            process_text_chunks(second_half_text, f"{output_name}_part2", tts, device)
        else:
            first_chunk_time = process_text_chunks(text, output_name, tts, device)

        print("\nAll processing complete!")
        return first_chunk_time
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return None
from TTS.api import TTS

def list_all_models():
    # Initialize TTS
    tts = TTS()
    
    # List all available models
    print("\nAvailable TTS Models:")
    print("====================")
    for model in tts.list_models()['tts']:
        print(f"- {model}")
    
    print("\nAvailable Vocoder Models:")
    print("=======================")
    for model in tts.list_models()['vocoder']:
        print(f"- {model}")
from TTS.api import TTS

if __name__ == "__main__":
    # Initialize TTS
    tts = TTS()
    
    # Get the ModelManager instance
    manager = tts.list_models()
    
    # Print all available models in a readable format
    print("\nAvailable TTS Models:")
    print("====================")
    for model_name in manager.list_tts_models():
        print(f"- {model_name}")
    
    print("\nAvailable Vocoder Models:")
    print("=======================")
    for model_name in manager.list_vocoder_models():
        print(f"- {model_name}")
    # print(TTS().list_models()
    # test_text = "This is a test of the text to speech system. It should play this audio."
    # text_to_speech(test_text)
   