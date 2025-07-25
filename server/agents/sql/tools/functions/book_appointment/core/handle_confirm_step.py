
import time
from typing import Dict
from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
from agents.sql.tools.functions.book_appointment.extract_patient_details import extract_patient_details
from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
from langchain.tools import StructuredTool
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.register_patient import run_register_patient
from agents.sql.tools.functions.find_best_match import find_best_match
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)
from agents.sql.tools.functions._build_response import _build_response


async def handle_confirm_step(input_str: str, collected_data: Dict) -> Dict:
        """Handle booking confirmation with proper response structure"""
        step_start_time = time.time()
        subactions = []

        try:
            # Extract confirmation
            llm_start = time.time()
            result = await extract_patient_info(input_str, 'confirmation')
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_confirmation",
                "reason": result["value"],
                "success": result['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not result['success'] or result['value'].lower() != 'yes':
                return _build_response(
                    "Booking process aborted successfully. If you need to book again, please start over.",
                    'get_doctor',

                    status='resolved',
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            collected_data["confirmation"] = result['value']
            return _build_response(
                "What is your Phone Number",
                'assure_registration',
                collected_data,
                # 'in_progress',
                # "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Error in confirmation step: {str(e)}")
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_confirmation_step",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred during confirmation. Please tell again your valid phone number.",
                'confirm_booking',
                collected_data,
                'error',
                "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
