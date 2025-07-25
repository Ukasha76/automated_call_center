from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from langchain.tools import StructuredTool
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agents.sql.tools.functions.create_prompt import create_prompt
import random
import string
import logging
import asyncio
from agents.sql.tools.functions._build_response import _build_response

import re
import json
from pydantic import Field
from supabase import create_client, Client
from typing import Union  # Python 3.9+

supabase: Client = create_client(
    supabase_url="https://adxmtyjibwipeivrxcil.supabase.co",
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkeG10eWppYndpcGVpdnJ4Y2lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NDU1NDEsImV4cCI6MjA0OTMyMTU0MX0.0XPdpUTpBkWAuOvsdShIrSj6V6_EyQJnAuJW1eprMb4"
)



logger = logging.getLogger(__name__)
async def create_patient_record(data: Dict) -> Dict:
    """
    Create a new patient record in the database
    """
    try:
        # Generate patient ID
        
        ALLOWED_FIELDS = {'name', 'gender', 'phone_number', 'age', 'address'}
        
        # Generate patient ID
        patient_id = ''.join(random.choices(string.digits, k=8))
        
        # Filter and validate required fields
        filtered_data = {
            field: str(data[field]) 
            for field in ALLOWED_FIELDS 
            if field in data
        }
        
        # Validate all required fields exist
        missing = ALLOWED_FIELDS - set(filtered_data.keys())
        if missing:
            return {
                'success': False,
                'value': f"Missing required fields: {', '.join(missing)}"
            }
        
        # Prepare final record
        patient_record = {
            "patient_id": patient_id,
            **filtered_data
        }
        
        # Insert into database
        result = supabase.table("patients").insert(patient_record).execute()
        
        if not result:
            raise Exception("Failed to save patient data")
        
        return {
            'success': True,
            'value': patient_id,
            'confidence': 1.0
        }
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return {
            'success': False,
            'value': f"Failed to create patient record: {str(e)}",
            'confidence': 0.0
        }
