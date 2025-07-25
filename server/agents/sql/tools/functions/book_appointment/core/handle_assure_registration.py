# appointment_steps/reason_handler.py

import time
from typing import Dict
from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
from agents.sql.tools.functions.book_appointment.extract_patient_details import extract_patient_details
from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
from langchain.tools import StructuredTool
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.register_patient import run_register_patient
from agents.sql.tools.functions.find_best_match import find_best_match
from agents.sql.tools.functions.book_appointment.utils.complete_booking import complete_booking

from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)
from agents.sql.tools.functions._build_response import _build_response

async def handle_assure_registration(input_str: str,collected_data: Dict) -> Dict:
        """Handle patient verification/registration with metrics and error handling"""
        step_start_time = time.time()
        subactions = []

        try:
            input_str = str(input_str).strip() if input_str else ""
            
            if not input_str:
                return _build_response(
                    "What is your phone number",
                    'assure_registration',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Extract phone number
            llm_start = time.time()
            result = await extract_patient_info(input_str, 'phone_number')
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_phone_number",
                "reason": result["value"],
                "success": result['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not result['success']:
                return _build_response(
                    "Please provide a valid phone number",
                    'assure_registration',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Check patient existence
            db_start = time.time()
            response = await extract_patient_details(result["value"])
            db_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "check_patient_existence",
                "success": response['success'],
                "reason": response.get("message", "Patient lookup"),
                "duration_ms": round((db_end - db_start) * 1000, 2)
            })
            
            collected_data['phone_number']=result["value"]
            if not response['success']:
                # Patient not found - initiate registration flow
                return _build_response(
                    "You are not a registered patient , lets register you first. What is your full name",
                    'registering',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Patient exists - store ID and complete booking
            logger.info(f"Patient already registered with ID: {response['value']}")
            collected_data["patient_id"] = response['value']
            
            return await complete_booking(collected_data)

        except Exception as e:
            logger.error(f"Error in registration assurance step: {str(e)}")
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_registration_assurance",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred while verifying your registration. Please tell me your phone number again.",
                'assure_registration',
                collected_data,
                'error',
                "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
 