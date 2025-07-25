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
async def handle_age_step(input_str: str, collected_data:Dict) -> Dict:
        """Handle age input step"""
        try:
            result = await extract_patient_info(input_str, 'age')
            
            if not result['success']:
                return _build_response(
                    result['value'],
                    'get_age',
                    collected_data,
                    'in_progress',
                    "patient_registration"
                )
            
            collected_data['age'] = result['value']
            
            return _build_response(
                "What is your address",
                'get_address',
                collected_data,
                'in_progress',
                "patient_registration"
            )
        except Exception as e:
            logger.error(f"Error in age step: {e}")
            return _build_response(
                    f"Error in age step: {e} , please tell me your age.",
                    'get_age',
                    collected_data,
                    'error',
                    "patient_registration"
                    # "cancel_appointment",
             
                
                )
