from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from langchain.tools import StructuredTool
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agents.sql.tools.functions.create_prompt import create_prompt
from agents.sql.tools.functions.register_patient.core.handle_name_step import handle_name_step
from agents.sql.tools.functions.register_patient.core.handle_address_step import handle_address_step
from agents.sql.tools.functions.register_patient.core.handle_age_step import handle_age_step
# from agents.sql.tools.functions.register_patient.core.handle_confiramtion_step import handle_confirmation_step
from agents.sql.tools.functions.register_patient.core.handle_gender_step import handle_gender_step
from agents.sql.tools.functions.book_appointment.utils.normalize_input import  normalize_input

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

class PatientRegistrationTool:
    def __init__(self):
        self.current_step = "get_name"
        self.collected_data = {}

    async def invoke(self, input_data: Any, context: Dict = None) -> Dict:
        """Main entry point with complete type safety"""
        try:
            # Debug what we received
            logger.debug(f"Raw input: {input_data} (type: {type(input_data)})")

            # Convert to safe format
            safe_input = normalize_input(input_data)
            
            # Extract values with guarantees
            query = str(safe_input['query_text'])
            ctx = safe_input.get('context', {}) or (context if isinstance(context, dict) else {})
            
            logger.debug(f"Processing - query: '{query}', context keys: {list(ctx.keys())}")
            return await self.handle_query(query, ctx)
            
        except Exception as e:
            logger.error(f"Invoke error: {str(e)}", exc_info=True)
            return {
                "output": f"System error: {str(e)}",
                "status": "error",
                "debug": {
                    "input_received": str(input_data)[:100],
                    "input_type": str(type(input_data))
                }
            }

    
    async def handle_query(self, input_str: str, context: Dict[str, Any]) -> Dict:
        """
        Handles the patient registration process.
        Returns dict with:
        - response: string for user
        - current_step: next step identifier
        - collected_data: updated context
        - status: 'in_progress'|'complete'|'error'
        """
        self.current_step = context.get('registration_substep', 'get_name')
        self.collected_data = context.get('registration_data', {})
        self.collected_data['phone_number'] = context.get('collected_data', {}).get('phone_number')
        # self.collected_data['phone_number']=context.get('collected_data').get('phone_number')

        try:

            if self.current_step == 'get_name':
                return await handle_name_step(input_str,self.collected_data)
            elif self.current_step == 'get_gender':
                return await  handle_gender_step(input_str,self.collected_data)
            elif self.current_step == 'get_age':
                return await  handle_age_step(input_str,self.collected_data)
            elif self.current_step == 'get_address':
                return await  handle_address_step(input_str,self.collected_data)
            elif self.current_step == 'confirm':
                return await  self._handle_confirmation_step(input_str)
            else:
                return self._reset_flow("Let's start your registration. What is your name?")
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return self._reset_flow("I encountered an error. Let's start over.")
    import re

    async def _handle_confirmation_step(self, input_str: str) -> Dict:
        """Handle final confirmation and registration"""
        try:
            result = await extract_patient_info(input_str, 'confirmation')
            
            if result['success']:
                if result['value'] == "yes":
                    record_result = await create_patient_record(self.collected_data)
                    if not record_result['success']:
                        return _build_response(
                            f"{record_result['value']}, lets try again. What is your name?",
                            'get_name',
                            self.collected_data,
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
                elif result['value'] == "no":
                    return _build_response(
                        "Registration aborted successfully. If you need to register again, please start over.",
                        None,
                        {},
                        'complete',
                        "patient_registration"
                    )
            else:
                return _build_response(
                    result['value'],
                    'confirm',
                    self.collected_data,
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
    def _reset_flow(self, message: str) -> Dict:
        """Reset the registration flow"""
        self.current_step = 'get_name'
        self.collected_data = {}
        return {
            message,
            'get_name',
            {},
            # 'status': 'in_progress'
        }

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



# Input schema for registration

# Create tool instance
# registration_tool = PatientRegistrationTool()

class PatientRegistrationInput(BaseModel):
    input: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Either a JSON string or dictionary containing 'query_text' and 'context'"
    )



import asyncio
from typing import Dict, Any, Union
import json
import logging
from functools import wraps

async def run_register_patient(query_text: str, context: Dict[str, Any]) -> str:
    """Async version of the registration function"""
    try:
        # Validate input
        if not isinstance(query_text, str) or not query_text.strip():
            raise ValueError("query_text must be a non-empty string")
        if not isinstance(context, dict):
            raise ValueError("context must be a dictionary")

        tool = PatientRegistrationTool()
        result = await tool.invoke({"query_text": query_text, "context": context})
        
        return result

    except Exception as e:
        error_msg = f"Registration failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "output": error_msg,
            "current_step": "get_name",
            "collected_data": {},
            "status": "error"
        })

__all__ = ["run_register_patient"]