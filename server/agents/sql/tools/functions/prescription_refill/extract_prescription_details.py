import logging
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)

supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)

async def extract_prescription_details(prescription_id: str) -> Dict[str, Any]:
    """
    Retrieves prescription details for the given prescription_id.

    Args:
        prescription_id: The unique identifier for the prescription

    Returns:
        Dictionary with:
        - success: Boolean indicating operation success
        - value: Either error message or formatted prescription details string
        - data: Raw prescription details (only when success=True)
    """
    try:
        if not prescription_id or not isinstance(prescription_id, str):
            logger.warning(f"Invalid prescription_id provided: {prescription_id}")
            return {
                "success": False,
                "value": "Please provide a valid prescription ID."
            }

        # Fetch prescription details
        prescription_query = supabase.table("prescriptions").select("*").eq("prescription_id", prescription_id).execute()


        if not prescription_query.data:
            logger.info(f"No prescription found for ID: {prescription_id}")
            return {
                "success": False,
                "value": "No prescription found with the provided ID."
            }
        
        prescription = prescription_query.data[0]
        if prescription["refills_remaining"] ==0:
            return {
                "success": False,
                "value": "No refill left. Please visit hospital",
                "refills_remaining":False
            }
        patient_id = prescription["patient_id"]
        doctor_name_value = prescription["prescribed_by"]  # this is actually doctor_name
        # refills_allowed = prescription["refills_allowed"]
        # refills_remaining = prescription["refills_remaining"]
        # start_date = prescription["start_date"]
        # end_date = prescription["end_date"]
        # medication_name = prescription["medication_name"]
        # dosage= prescription[""]

        # Fetch patient name
        patient_query = supabase.table("patients").select("name").eq("patient_id", patient_id).execute()
        if not patient_query.data:
            logger.error(f"Patient not found for ID: {patient_id}")
            return {
                "success": False,
                "value": "Could not retrieve patient information."
            }

        patient_name = patient_query.data[0]["name"]

        # doctor_name is stored in the "prescribed_by" field, no need to fetch from doctors table
        doctor_name = doctor_name_value

        # Format success message
        formatted_response = (
            f"Prescription Details are ,"
            f"Patient is {patient_name}."
            f"Prescribed by Dr. {doctor_name}."
            f"Medication is {prescription['medication_name']}."
            f"Dosage is {prescription['dosage']}."
            # f"Start Date: {prescription['start_date']}\n"
            # f"End Date: {prescription['end_date']}\n"
            # f"Refills Allowed: {prescription['refills_allowed']}\n"
            f"Refills Remaining are {prescription['refills_remaining']}."
        )

        return {
            "success": True,
            "value": formatted_response,
            "prescription_id": prescription_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            **prescription
        }

    except Exception as e:
        logger.error(f"Error fetching prescription details: {str(e)}", exc_info=True)
        return {
            "success": False,
            "value": "An error occurred while fetching prescription details. Please try again later."
        }

__all__ = ["extract_prescription_details"]
