import uuid
from typing import Dict, Any
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)
def split_day_time(input_str):
            """Splits 'Day Time' into separate components"""
            try:
                # Split on first space only
                day, time = input_str.split(' ', 1)
                return day.strip(), time.strip()
            except ValueError:
                # Handle cases where input doesn't contain a space
                return "", input_str.strip() if input_str else ("", "")

async def create_appointment_record(data: Dict) -> Dict:
    """
    Create a new appointment record
    
    Args:
        data (Dict): Dictionary containing appointment information
        
    Returns:
        Dict: Dictionary containing appointment details
    """
    try:
        supabase = create_client(
            supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
            supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
        )
        
        day, time = split_day_time(data['selected_time'])

        print(f"Day: {day}")    # Output: Day: Monday
        print(f"Time: {time}")  # Output: Time: 10pm

       
        appointment_id = str(uuid.uuid4())
        doctor_id = int(data["doctor_id"])
        patient_id = (data.get("patient_id", 6078300))

        # Create appointment data
        appointment = {
            'patient_id': patient_id,
            'doctor_id':doctor_id,
            'reason': data['reason'],
            'appointment_day': day,
            'appointment_time': time
            
        }
        # response = supabase.table("appointments").insert(appointment).execute()
        response = supabase.table("appointments").insert(appointment).execute()
        appointment_id = response.data[0]["appointment_id"]
        # Log the creation
        logger.info(f"Created appointment: {appointment}")
        
        return {
            "success": True,
            "value": response
        }
        
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        return {
            "success": False,
            "value": str(e)
        }
