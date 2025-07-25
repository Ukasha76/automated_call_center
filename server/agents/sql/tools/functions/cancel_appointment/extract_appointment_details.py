
import logging
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)
supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)
async def extract_appointment_details(appointment_id: str) -> Dict[str, Any]:
    """
    Retrieves appointment details for the given appointment_id.
    
    Args:
        appointment_id: The unique identifier for the appointment
        supabase: Authenticated Supabase client instance
        
    Returns:
        Dictionary with:
        - success: Boolean indicating operation success
        - value: Either error message or formatted appointment details string
        - data: Raw appointment details (only when success=True)
    """
    try:
        # Validate input
        if not appointment_id or not isinstance(appointment_id, str):
            logger.warning(f"Invalid appointment_id provided: {appointment_id}")
            return {
                "success": False,
                "value": "Please provide a valid appointment ID."
            }

        # Fetch appointment details
        appointment_query = supabase.table("appointments").select(
            "patient_id", "doctor_id", "appointment_day", "appointment_time", "reason"
        ).eq("appointment_id", appointment_id).execute()

        if not appointment_query.data:
            logger.info(f"No appointment found for ID: {appointment_id}")
            return {
                "success": False,
                "value": "No booking found with the provided ID."
            }

        appointment = appointment_query.data[0]
        doctor_id = appointment["doctor_id"]
        patient_id = appointment["patient_id"]
        reason = appointment["reason"]

        # Fetch patient details
        patient_query = supabase.table("patients").select(
            "name"
        ).eq("patient_id", patient_id).execute()

        if not patient_query.data:
            logger.error(f"Patient not found for ID: {patient_id}")
            return {
                "success": False,
                "value": "Could not retrieve patient information."
            }

        # Fetch doctor details
        doctor_query = supabase.table("doctors").select(
            "name"
        ).eq("doctor_id", doctor_id).execute()

        if not doctor_query.data:
            logger.error(f"Doctor not found for ID: {doctor_id}")
            return {
                "success": False,
                "value": "Could not retrieve doctor information."
            }

        # Extract data
        patient_name = patient_query.data[0]["name"]
        doctor_name = doctor_query.data[0]["name"]
        day = appointment["appointment_day"]
        time = appointment["appointment_time"]

        # Format success response
        formatted_response = (
            f"We found your booking details:\n\n"
            f"Patient: {patient_name}\n"
            f"Appointment with Dr. {doctor_name}\n"
            f"Date: {day}\n"
            f"Time: {time}"
        )

        return {
            "success": True,
            "value": formatted_response,
            "appointment_id":appointment_id,
            "patient_id":patient_id,
            "doctor_id":doctor_id,
            "patient_name":patient_name,
            "doctor_name":doctor_name,
            "day":day,
            "time":time,
            "reason":reason
        }

    except Exception as e:
        logger.error(f"Error fetching appointment details: {str(e)}", exc_info=True)
        return {
            "success": False,
            "value": "An error occurred while fetching appointment details. Please try again later."
        }

__all__ = ["extract_appointment_details"]