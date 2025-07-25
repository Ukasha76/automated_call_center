from supabase import create_client, Client
from rapidfuzz import process

supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)



# async def find_best_match(input_name: str) -> str:
#     """
#     Finds and returns the most similar doctor name from the stored doctor list.
#     """
#     threshold = 70
#     try:
#         # Fetch all doctor names from Supabase
#         response = supabase.table("doctors").select("name","doctor_id").execute()

#         if not response.data:
#             return ""  # No doctors in DB

#         doctor_names = [doc["name"] for doc in response.data]
#         doctor_ids = [doc["doctor_id"] for doc in response.data]

#         best_match, score, _ = process.extractOne(input_name, doctor_names) if doctor_names else (None, 0, None)

#         return best_match if best_match and score >= threshold else ""

#     except Exception as e:
#         return ""  # Return empty string on error

# __all__ = ["find_best_match"]

async def find_best_match(input_name: str) ->dict:
    """
    Finds and returns the most similar doctor name and ID from the stored doctor list.
    Returns tuple of (best_match_name, doctor_id) or empty strings if no match found.
    """
    threshold = 70
    try:
        # Fetch all doctor names and IDs from Supabase
        response = supabase.table("doctors").select("name", "doctor_id").execute()

        if not response.data:
            return ("", "")  # No doctors in DB

        doctor_names = [doc["name"] for doc in response.data]
        doctor_info = {doc["name"]: doc["doctor_id"] for doc in response.data}

        best_match, score, _ = process.extractOne(input_name, doctor_names) if doctor_names else (None, 0, None)


        if best_match and score >= threshold:
            return {
                "success":True,
                "name": best_match,
                
                "doctor_id": doctor_info.get(best_match, "")
            }
        else:
            return {"success":False ,"name": "No match found", "doctor_id": ""}
    except Exception as e:
        return {"success":False ,"name": "", "doctor_id": ""}


__all__ = ["find_best_match"]