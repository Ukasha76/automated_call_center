from datetime import datetime, timedelta
import logging
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)

supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)
async def update_prescription_record(prescription_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prescription_id = prescription_data["prescription_id"]
        current_remaining = prescription_data["refills_remaining"]

        if current_remaining <= 0:
            return {
                "success": False,
                "value": "No refills remaining for this prescription."
            }

        updated_remaining = current_remaining - 1
        
        if updated_remaining < 0:
            updated_remaining = 0


        update_result = supabase.table("prescriptions").update({
            "refills_remaining": updated_remaining
        }).eq("prescription_id", prescription_id).execute()


       

# For SQL INSERT/UPDATE:
        valid_until = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

        insert_result = supabase.table("approved_refills").insert({
            "prescription_id": prescription_id,
            "valid_until": valid_until,
            "status": "in_process",
            "pickup_location": "pharmacy",
            "medication_name": prescription_data["medication_name"],
            "dosage": prescription_data["dosage"]
        }).execute()

        if not insert_result.data:
            logger.error("Failed to insert into approved_refills.")
            return {
                "success": False,
                "value": "Failed to record refill approval."
            }

        refill_id = insert_result.data[0].get("refill_id")

        return {
            "success": True,
            "value": f"Refill recorded successfully with ID: {refill_id}",
            "refill_id": refill_id,
            "valid_until": valid_until
        }

    except Exception as e:
        logger.error(f"Error in update_prescription_record: {str(e)}", exc_info=True)
        return {
            "success": False,
            "value": "An error occurred while processing the refill."
        }

__all__ = ["update_prescription_record"]