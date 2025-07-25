# from ....connection import supabase  # Make sure this is an AsyncSupabaseClient
from supabase import create_client, Client
import asyncio
import httpx
# from rapidfuzz import process

async def get_available_slots( doctor_id: str )->dict:
    """
    Fetches available appointment slots for a given doctor (searched by name), excluding booked slots.
    Returns a dictionary with success flag and either slot list or error message.
    """
    try:
        # Create client inside the function to ensure fresh connection
        supabase = create_client(
            supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
            supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
        )

        # Fetch doctor_id using doctor_name
        # doctor_response = supabase.table("doctors").select("doctor_id").eq("name", doctor_name).execute()
          
        # if not doctor_response.data:
        #     return {
        #         "success": False,
        #         "value": f"Doctor '{doctor_name}' not found."
        #     }

        # doctor_id = doctor_response.data[0]["doctor_id"]
    
        # Fetch all available slots
        slots_query = supabase.table("doctors_slots").select("day, time").eq("doctor_id", doctor_id).execute()
       
# Standardize day names to lowercase for consistent comparison
        all_slots = {(slot["day"].lower(), slot["time"]) for slot in slots_query.data} if slots_query.data else set()
                # Fetch booked slots
        # Fetch booked slots from appointments table
        booked_query = supabase.table("appointments").select("appointment_day, appointment_time").eq("doctor_id", doctor_id).execute()

# Standardize day names to lowercase for consistent comparison
        booked_slots = {(slot["appointment_day"].lower(), slot["appointment_time"]) for slot in booked_query.data} if booked_query.data else set()

        # Calculate available slots
                
        # Calculate available slots by removing booked slots
        available_slots = all_slots - booked_slots

        if not available_slots:
            return {
                "success": False,
                "value": "No available slots."
            }
        

        return {
            "success": True,
            "value": sorted(list(available_slots))
        }

    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Add debug print
        return {
            "success": False,
            "value": f"Error fetching slots: {str(e)}"
        }

# def main():
#     # Test with a doctor name
#     doctor_name = "Angela Webb"  # Replace with an actual doctor name from your database
#     result = get_available_slots(doctor_name)
#     print("\nTest Results:")
#     print(f"Doctor: {doctor_name}")
#     print(f"Success: {result['success']}")
#     print(f"Value: {result['value']}\n")

# if __name__ == "__main__":
#     main()

__all__ = ["get_available_slots"]
