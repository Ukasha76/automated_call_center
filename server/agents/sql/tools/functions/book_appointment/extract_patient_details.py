import uuid
from typing import Dict, Any
import logging
from supabase import create_client, Client
logger = logging.getLogger(__name__)

async def extract_patient_details(phone_number: str) -> Dict:
    """
    Search for patient details based on phone number and return patient_id
    
    Args:
        phone_number (str): Patient's phone number for lookup
        
    Returns:
        Dict: Dictionary containing patient details or error information
    """
    try:
        supabase = create_client(
            supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
            supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
        )
        
        # Query patient by phone number
        response = supabase.table("patients").select("patient_id").eq("phone_number", phone_number).execute()
        
        if not response.data:
            logger.info(f"No patient found with phone: {phone_number}")
            return {
                "success": False,
                "value": "Patient not found",
                "exists": False
            }
        
        patient_id = response.data[0]["patient_id"]
        logger.info(f"Found patient ID: {patient_id} for phone: {phone_number}")
        
        return {
            "success": True,
            "value": patient_id,
            "exists": True
        }
        
    except Exception as e:
        logger.error(f"Error searching for patient: {str(e)}")
        return {
            "success": False,
            "value": str(e),
            "exists": False
        }