

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

async def handle_name_step(input_str: str, collected_data:Dict) -> Dict:
        """Comprehensive name handling with all validation built-in"""
        # Clean and prepare input
        input_str = str(input_str).strip() if input_str else ""
        
        # Case 1: Empty input at start of registration
        if not input_str and not collected_data.get('name'):
            return _build_response(
                "Lets register a new patient. What is the patient name?",
                'get_name',
                collected_data,
                'in_progress',
                "patient_registration"
            )

        name_result = await extract_patient_info(input_str, 'name')
        
        if not name_result['success'] or name_result['value'] in ['""', "''"]:
            return _build_response(
                "I did not catch the name. Please tell  the patient name.",
                'get_name',
                collected_data,
                'in_progress',
                "patient_registration"
            )
        
        collected_data['name'] = name_result['value']
        
        return _build_response(
            "What is  gender, (Male ,Female ,Other)",
            'get_gender',
            collected_data,
            'in_progress',
            "patient_registration"
        )
