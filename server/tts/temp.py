# # import os
# # from TTS.api import TTS
# # import torch

# # # Get the current script's directory
# # script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()

# # # Check GPU availability
# # if torch.cuda.is_available():
# #     device_name = torch.cuda.get_device_name(0)
# #     print(f"CUDA is available. Using GPU: {device_name}")
# #     gpu_flag = True
# # else:
# #     print("CUDA is not available. Falling back to CPU.")
# #     gpu_flag = False

# # # Initialize the TTS model with proper device handling
# # try:
# #     tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=gpu_flag)
# #     print("TTS model initialized successfully")
# # except Exception as e:
# #     print(f"Error initializing TTS model: {e}")
# #     exit(1)

# # # Output file path in the same directory as the script
# # output_path = os.path.join(script_dir, "output.wav")

# # # Generate speech and save to the script's directory
# # try:
# #     tts.tts_to_file(
# #         text="HI how may i help you",
# #         file_path=output_path,
# #         split_sentences=False  # Disabling splitting for better performance
# #     )
# #     print(f"Audio successfully saved to: {output_path}")
# # except Exception as e:
# #     print(f"Error generating speech: {e}")
# import os
# import time
# import pandas as pd
# from TTS.api import TTS
# import torch

# # Initialize TTS with GPU if available
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")

# tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=(device == "cuda"))

# # Load the Excel file
# excel_path = "queries.xlsx"
# df = pd.read_excel(excel_path)

# # Create output directory if it doesn't exist
# output_dir = "tts_outputs"
# os.makedirs(output_dir, exist_ok=True)

# # Process each row
# for index, row in df.iterrows():
#     response_text = str(row['response'])  # Ensure it's a string
    
#     # Generate unique filename
#     output_filename = f"response-{index+1}.wav"
#     output_path = os.path.join(output_dir, output_filename)
    
#     print(f"Processing row {index+1}/{len(df)}...")
    
#     try:
#         # Measure TTS time
#         start_time = time.time()
        
#         tts.tts_to_file(
#             text=response_text,
#             file_path=output_path,
#             split_sentences=False
#         )
#         end_time = time.time()
#         transcription_time = end_time - start_time
        
#         # Update DataFrame
#         df.at[index, 'transcription_time'] = transcription_time
#         print(f"Saved {output_filename} | Time: {transcription_time:.2f}s")
        
#         # Save progress every 10 rows
#         if (index + 1) % 5 == 0:
#             df.to_excel(excel_path, index=False)
#             print("Progress saved to Excel file")
    
#     except Exception as e:
#         print(f"Error processing row {index+1}: {str(e)}")
#         df.at[index, 'transcription_time'] = "ERROR"
#         continue

# # Final save
# df.to_excel(excel_path, index=False)
# print("Processing complete. All results saved to Excel file.")

# import os
# import time
# from TTS.api import TTS
# import torch

# # Initialize TTS with GPU if available
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")

# tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=(device == "cuda"))

# # Create output directory if it doesn't exist
# output_dir = "tts_outputs"
# os.makedirs(output_dir, exist_ok=True)

# # Query to synthesize (repeated 3 times)
# query = """I can help with that!

# Hi there. To be admitted to Osaka University Hospital, you ll need to follow these steps according to the Hospital Admission Process and Admission Guidelines and Procedures:

# Get the Date
# Your doctor will inform you of the date you need to be admitted. If the admission is required after an outpatient visit, your doctor will register the admission, and the clinical section will contact you with the specific time.

# Gather Your Documents
# Ensure you have your patient registration card, personal seal, and admission application form ready. You can find more details about required materials in the Hospital Admission Process.

# Arrive at Inpatients Reception
# On the day of admission, go to the Inpatients Reception with all your documents.

# Complete Admission
# You or a representative will need to complete the admission procedure before going to your ward."""

# queries = [query] * 3
# transcription_times = []

# # Process each query
# for i, text in enumerate(queries, start=1):
#     print(f"Processing query {i}/3...")
    
#     output_filename = f"response_{i}.wav"
#     output_path = os.path.join(output_dir, output_filename)
    
#     try:
#         start_time = time.time()
        
#         tts.tts_to_file(
#             text=text,
#             file_path=output_path,
#             split_sentences=False
#         )
        
#         elapsed_time = time.time() - start_time
#         transcription_times.append(elapsed_time)
#         print(f"Saved {output_filename} | Time: {elapsed_time:.2f}s")
    
#     except Exception as e:
#         print(f"Error processing query {i}: {e}")
#         transcription_times.append("ERROR")

# # Print summary
# print("\n--- Transcription Times ---")
# for i, t in enumerate(transcription_times, start=1):
#     print(f"Query {i}: {t if t != 'ERROR' else 'Failed'} seconds")
import os
import time
from TTS.api import TTS
import torch

# Initialize TTS with GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device.upper()}")

# Load model only once at the beginning
print("Loading TTS model...")
start_load = time.time()
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=(device == "cuda"))
load_time = time.time() - start_load
print(f"Model loaded in {load_time:.2f} seconds\n")

# Create output directory if it doesn't exist
output_dir = "tts_outputs"
os.makedirs(output_dir, exist_ok=True)

# Query to synthesize (repeated 3 times)
query = """I can help with that Hi there. To be admitted to Osaka University Hospital, you ll need to follow these steps according to the Hospital Admission Process and Admission Guidelines and Procedures:Get the Date Your doctor will inform you of the date you need to be admitted. If the admission is required after an outpatient visit, your doctor will register the admission, and the clinical section will contact you with the specific time.Gather Your DocumentsEnsure you have your patient registration card, personal seal, and admission application form ready. You can find more details about required materials in the Hospital Admission Process.Arrive at Inpatients ReceptionOn the day of admission, go to the Inpatients Reception with all your documents.Complete Admission You or a representative will need to complete the admission procedure before going to your ward."""
queries = [query] * 3
transcription_times = []

# Warm-up run (optional, to initialize CUDA context etc.)
print("Running warm-up inference...")
tts.tts_to_file(text="Warm-up run.", file_path=os.path.join(output_dir, "warmup.wav"))

# Process each query
for i, text in enumerate(queries, start=1):
    print(f"Processing query {i}/3...")
    
    output_filename = f"response_{i}.wav"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        start_time = time.time()
        
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            split_sentences=False
        )
        
        elapsed_time = time.time() - start_time
        transcription_times.append(elapsed_time)
        print(f"Saved {output_filename} | Time: {elapsed_time:.2f}s")
    
    except Exception as e:
        print(f"Error processing query {i}: {e}")
        transcription_times.append("ERROR")

# Print summary
print("\n--- Summary ---")
print(f"Model load time: {load_time:.2f} seconds")
print("\n--- Transcription Times ---")
for i, t in enumerate(transcription_times, start=1):
    print(f"Query {i}: {t if t != 'ERROR' else 'Failed'} seconds")

avg_time = sum(t for t in transcription_times if t != "ERROR") / len(transcription_times)
print(f"\nAverage transcription time: {avg_time:.2f} seconds")