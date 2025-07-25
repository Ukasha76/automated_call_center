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


async def handle_reason_step(input_str: str, context: Dict, collected_data: Dict) -> Dict:
    step_start_time = time.time()
    subactions = []

    try:
        input_str = str(input_str).strip() if input_str else ""

        if not input_str:
            return _build_response(
                "Please provide a reason for your appointment.",
                'get_reason',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        llm_start = time.time()
        reason_result = await extract_patient_info(input_str, 'reason')
        llm_end = time.time()

        subactions.append({
            "action_type": "llm",
            "action_name": "extract_appointment_reason",
            "reason": reason_result["value"],
            "success": reason_result['success'],
            "duration_ms": round((llm_end - llm_start) * 1000, 2),
        })

        if not reason_result['success']:
            return _build_response(
                f"Could not understand reason the  {reason_result.get('value', 'Unknown error')} , please provide a clear reason for your appointment.",
                'get_reason',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        collected_data["reason"] = reason_result['value']

        confirmation_msg = (
            f"Do you want an appointment with Doctor {context.get('collected_data').get('doctor')} "
            f"(yes/no)"
        )

        formated_response= await extract_patient_info(confirmation_msg,'format_response')

        return _build_response(
            confirmation_msg,
            'confirm_booking',
            collected_data,
            step_metrics={
                "subactions": subactions,
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
            }
        )

    except Exception as e:
        logger.error(f"Error in reason step: {str(e)}")
        subactions.append({
            "action_type": "error",
            "action_name": "exception_in_reason_step",
            "success": False,
            "duration_ms": round((time.time() - step_start_time) * 1000, 2)
        })

        return _build_response(
            "An error occurred while processing your reason. Please tell again the reason for your appointment.",
            'get_reason',
            collected_data,
            'error',
            "booking_appointment",
            step_metrics={
                "subactions": subactions,
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
            }
        )
