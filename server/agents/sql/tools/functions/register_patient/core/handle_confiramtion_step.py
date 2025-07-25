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
from agents.sql.tools.functions.register_patient.utils.create_patient_record import create_patient_record

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

async def _handle_confirmation_step(input_str: str, collected_data:Dict) -> Dict:
        """Handle final confirmation and registration"""
        try:
            result = await extract_patient_info(input_str, 'confirmation')
            
            if result['success']:
                if result['value'] == "yes":
                    record_result = await create_patient_record(collected_data)
                    if not record_result['success']:
                        return _build_response(
                            record_result['value'],
                            'get_name',
                            {},
                            'error',
                            "patient_registration"
                        )
                    return _build_response(
                        record_result['value'],
                        None,
                        {},
                        'complete',
                        "patient_registration"
                    )
                # will modify ths later to reset if user say no
                elif result['value'] == "no":
                    return _build_response(
                    f"The registration process aborted successfully.",
                    None,
                    None,
                    'resolved',
                    # "cancel_appointment",
                )
            else:
                return _build_response(
                    result['value'],
                    'confirm',
                    collected_data,
                    'in_progress',
                    "patient_registration"
                )

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return _build_response(
                "Sorry, I couldn't complete your registration. Please try again.",
                'get_name',
                {},
                'error',
                "patient_registration"
            )