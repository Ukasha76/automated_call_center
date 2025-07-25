
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


async def handle_doctor_step(input_str: str, collected_data: Dict) -> Dict:
    step_start_time = time.time()
    subactions = []

    try:
        input_str = str(input_str).strip() if input_str else ""

        if not input_str:
            return _build_response(
                "Which doctor would you like to see. Please provide their full name",
                'get_doctor',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        llm_start = time.time()
        name_result = await extract_patient_info(input_str, 'doctor_name')
        llm_end = time.time()

        subactions.append({
            "action_type": "llm",
            "action_name": "extract_doctor_name",
            "reason": name_result["value"],
            "success": name_result['success'],
            "duration_ms": round((llm_end - llm_start) * 1000, 2),
        })

        if not name_result['success']:
            return _build_response(
                f"{name_result['value']}, please tell me the full name of the doctor you want to see.",
                'get_doctor',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        db_start = time.time()
        response = await find_best_match(name_result["value"])
        db_end = time.time()

        subactions.append({
            "action_type": "db",
            "action_name": "find_doctor_match",
            "success": bool(response.get("name")),
            "reason": response.get("message", "Doctor lookup"),
            "duration_ms": round((db_end - db_start) * 1000, 2)
        })

        if not response.get("name"):
            return _build_response(
                "Could not find doctor. Which doctor would you like to book an appointment with",
                'get_doctor',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        doctor_name = response["name"]
        doctor_id = response["doctor_id"]

        slots_start = time.time()
        slots_result = await get_available_slots(doctor_id)
        slots_end = time.time()

        subactions.append({
            "action_type": "db",
            "action_name": "get_available_slots",
            "success": slots_result.get("success", False),
            "reason": slots_result.get("message", "Slot availability check"),
            "duration_ms": round((slots_end - slots_start) * 1000, 2)
        })

        if not slots_result.get("success"):
            return _build_response(
                f"Doctor {doctor_name} has no available slots currently.",
                status="resolved",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        slots_formatted = "\n".join(f"- {slot[0]} at {slot[1]}" for slot in slots_result["value"])
        formated_response= await extract_patient_info(slots_result['value'],'format_response')

        collected_data.update({
            "doctor": doctor_name,
            "doctor_id": doctor_id,
            "available_slots": formated_response['value']
        })

        return _build_response(
            f'Available slots for Doctor {doctor_name} are at {formated_response["value"]} . Please specify your preferred time from the available slots.',
            'get_time',
            collected_data,
            step_metrics={
                "subactions": subactions,
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
            }
        )

    except Exception as e:
        logger.error(f"Error in doctor selection step: {str(e)}", exc_info=True)
        subactions.append({
            "action_type": "error",
            "action_name": "exception_in_doctor_step",
            "success": False,
            "duration_ms": round((time.time() - step_start_time) * 1000, 2)
        })

        return _build_response(
            "An error occurred while processing the doctor selection. Please tell again the name of the doctor you want to see.",
            'get_doctor',
            collected_data,
            'error',
            step_metrics={
                "subactions": subactions,
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
            }
        )
