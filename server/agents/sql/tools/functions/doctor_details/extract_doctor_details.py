# from ....functions.find_best_match import find_best_match
# from ....functions.create_prompt import create_prompt
from supabase import create_client, Client

supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)


async def extract_doctor_details(user_input: str = None) -> dict:
    try:
 

        # Fetch doctor details from the database
        response = supabase.table("doctors").select("*").eq("name", user_input).single().execute()

        if response.data:
            return {
                'success': True,
                'value': response.data  # Return all doctor details
            }

        return {
            'success': False,
            'value': "Could not fetch doctor details. Please try again."
        }

    except Exception as e:
        return {
            'success': False,
            
            'value': f"Error retrieving doctor details: {str(e)}"
        }

__all__ = ["extract_doctor_details"]