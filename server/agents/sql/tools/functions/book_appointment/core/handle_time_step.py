 
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
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)
from agents.sql.tools.functions._build_response import _build_response

async def handle_time_step(input_str: str, collected_data: Dict) -> Dict:
        """Handle time selection step with validation and metrics"""
        step_start_time = time.time()
        subactions = []

        try:
            input_str = str(input_str).strip() if input_str else ""
            
            if not input_str:
                return _build_response(
                    "Please specify your preferred time from the available slots.",
                    'get_time',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Extract and validate time
            llm_start = time.time()
            time_result = await extract_patient_info(input_str, 'appointment_time', collected_data["available_slots"])
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_appointment_time",
                "reason": time_result["value"],
                "success": time_result['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            
            if not time_result['success']:
                return _build_response(
                    f"Could not find appointment time  {time_result.get('value', 'Unknown error')} Please choose a time from the available slots that are{ collected_data.get('available_slots', [])}.",
                    'get_time',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            collected_data["selected_time"] = time_result['value']

            return _build_response(
                "What is the reason for your appointment",
                'get_reason',
                collected_data,
                # 'in_progress',
                # "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Error in time selection step: {str(e)}")
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_time_step",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred while processing your time selection. Please choose a time from the available slots that are{ collected_data.get('available_slots', [])}.",
                'get_time',
                collected_data,
                # 'error',
                # "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )