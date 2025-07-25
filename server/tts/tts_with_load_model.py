# import torch
# from TTS.api import TTS
# import os
# import time
# import torchaudio
# from pydub import AudioSegment
# from pydub.playback import play

# # Select device (GPU or CPU) and print status
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")

# # Initialize TTS model
# tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch", progress_bar=False).to(device)

# # Text to synthesize
# full_text = """I can help with that!

# Hi there. To be admitted to Osaka University Hospital, you ll need to follow these steps according to the Hospital Admission Process and Admission Guidelines and Procedures:

# Get the Date
# Your doctor will inform you of the date you need to be admitted. If the admission is required after an outpatient visit, your doctor will register the admission, and the clinical section will contact you with the specific time.
# Gather your documents.

# Ensure you have your patient registration card, personal seal, and admission application form ready. You can find more details about required materials in the Hospital Admission Process.

# Arrive at Inpatients Reception
# On the day of admission, go to the Inpatients Reception with all your documents.

# Complete Admission
# You or a representative will need to complete the admission procedure before going to your ward."""

# # Count total words
# all_words = full_text.split()
# total_words = len(all_words)
# halfway_point = total_words // 2
# first_half_text = ' '.join(all_words[:halfway_point])

# print(f"Total words: {total_words}")
# print(f"Processing first half ({halfway_point} words)...")

# # Output path
# current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
# output_path = os.path.join(current_dir, "first_half_output.wav")

# # Split text into optimized chunks
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

# text_chunks = split_text_optimized(first_half_text)
# print(f"Split into {len(text_chunks)} optimal chunks")

# # Process chunks with detailed tracking
# wav_chunks = []
# start_time = time.time()
# processed_chars = 0
# total_chars = len(first_half_text)

# for i, chunk in enumerate(text_chunks, 1):
#     chunk_start = time.time()
#     processed_chars += len(chunk)
    
#     # Generate audio for this chunk
#     chunk_path = f"temp_chunk_{i}.wav"
#     tts.tts_to_file(text=chunk, file_path=chunk_path)
    
#     # Load and process the chunk
#     audio, sample_rate = torchaudio.load(chunk_path)
#     wav_chunks.append(audio)
#     os.remove(chunk_path)
    
#     # Progress tracking
#     chunk_time = time.time() - chunk_start
#     progress_percent = (processed_chars / total_chars) * 100
    
#     if i == 1:
#         first_chunk_time = time.time() - start_time
#         print(f"\nTime to first chunk: {first_chunk_time:.2f}s")
    
#     print(f"Chunk {i}/{len(text_chunks)} | {len(chunk.split())} words | "
#           f"Progress: {progress_percent:.1f}% | Time: {chunk_time:.2f}s")

# # Combine all chunks
# if wav_chunks:
#     full_audio = torch.cat(wav_chunks, dim=1)
#     torchaudio.save(output_path, full_audio, sample_rate)
    
#     total_time = time.time() - start_time
#     audio_length = full_audio.shape[1] / sample_rate
    
#     print(f"\n{'='*40}")
#     print(f"Total words processed: {halfway_point}/{total_words}")
#     print(f"Total processing time: {total_time:.2f}s")
#     print(f"Audio duration: {audio_length:.2f}s")
#     print(f"Real-time factor: {total_time/audio_length:.2f}")
#     print(f"Output saved to: {output_path}")
#     print(f"{'='*40}")
    
#     # Play the result
#     try:
#         audio = AudioSegment.from_wav(output_path)
#         print("\nPlaying generated audio...")
#         play(audio)
#     except Exception as e:
#         print(f"\nCouldn't play audio: {str(e)}")
# else:
#     print("No audio was generated")