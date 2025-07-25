# from typing import Dict, Any
# import logging

# logger = logging.getLogger(__name__)

# async def delete_appointment_record(appointment_id: str) -> Dict:
#     """
#     Delete an appointment record
    
#     Args:
#         appointment_id (str): ID of the appointment to delete
        
#     Returns:
#         Dict: Dictionary containing deletion result
#     """
#     try:
#         # This is a simplified example - in production you'd update the database
#         # Here we just simulate the deletion
#         logger.info(f"Deleting appointment with ID: {appointment_id}")
        
#         return {
#             'success': True,
#             'value': f"Appointment {appointment_id} has been successfully cancelled",
#             'confidence': 1.0
#         }
        
#     except Exception as e:
#         logger.error(f"Error deleting appointment: {str(e)}")
#         return {
#             'success': False,
#             'value': f"An error occurred while cancelling the appointment: {str(e)}",
#             'confidence': 0.0
#         }
import logging
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)
supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)


async def delete_appointment_record(appointment_id: str) -> Dict[str, Any]:
    """
    Deletes an appointment from the database.
    
    Args:
        appointment_id: The ID of the appointment to delete
        supabase: Authenticated Supabase client instance
        
    Returns:
        Dictionary with:
        - success: Boolean indicating if deletion was successful
        - value: Success message or error description
        - confidence: Confidence score (0.0-1.0) in the operation
    """
    # Input validation
    if not appointment_id or not isinstance(appointment_id, str):
        logger.warning(f"Invalid appointment_id provided: {appointment_id}")
        return {
            'success': False,
            'value': "Invalid appointment ID provided",
            'confidence': 0.0
        }

    try:
        # Execute deletion
        response = supabase.table("appointments")\
                         .delete()\
                         .eq("appointment_id", appointment_id)\
                         .execute()

        # Check if deletion was successful
        if not response.data:
            logger.error(f"No data returned when deleting appointment {appointment_id}")
            return {
                'success': False,
                'value': "Appointment not found or already deleted",
                'confidence': 0.8  # High confidence the appointment didn't exist
            }

        logger.info(f"Successfully deleted appointment {appointment_id}")
        return {
            'success': True,
            'value': f"Appointment {appointment_id} has been successfully cancelled",
            'confidence': 1.0,
            'data': response.data  # Include raw response data
        }
        
    except Exception as e:
        logger.error(f"Error deleting appointment {appointment_id}: {str(e)}", exc_info=True)
        return {
            'success': False,
            'value': f"Database error occurred while cancelling the appointment",
            'confidence': 0.3  # Low confidence due to unknown error state
        }

__all__ = ["delete_appointment_record"]