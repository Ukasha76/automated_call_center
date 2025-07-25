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
async def handle_address_step(input_str: str, collected_data:Dict) -> Dict:
        """Handle address input step"""
        try:
            result = await extract_patient_info(input_str, 'address')
            
            if not result['success']:
                return _build_response(
                    result['value'],
                    'get_address',
                    collected_data,
                    'in_progress',
                    "patient_registration"
                )
            
            collected_data['address'] = result['value']
            
            confirmation_message = (
                f"Please confirm your details:"
                f"Name: {collected_data['name']}."
                f"Gender: {collected_data['gender']}."
                f"Phone: {collected_data['phone_number']}."
                f"Age: {collected_data['age']}."
                f"Address: {collected_data['address']}.\n\n"
                f"Is this correct? (yes/no)"
            )
            # format_response = await extract_patient_info(confirmation_message, 'format_response')

            return _build_response(
                confirmation_message,
                'confirm',
                collected_data,
                'in_progress',
                "patient_registration"
            )
        except Exception as e:
            logger.error(f"Error in address step: {e}")
            return _build_response(
                    f"Error in address step: {e} , please tell me your address.",
                    'get_address',
                    collected_data,
                    'error',
                    "patient_registration"
                    # "cancel_appointment",
             
                
                )
