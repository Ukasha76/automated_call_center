import time
from typing import Dict
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.functions.find_best_match import find_best_match
from agents.sql.tools.functions._build_response import _build_response
from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots 
   
import logging

logger = logging.getLogger(__name__)

async def get_appointment_slots(input_str: str, context: Dict = None) -> Dict:
        step_start_time = time.time()
        subactions = []

        try:
            # 1. Extract name using LLM
            llm_start = time.time()
            name_extracted = await extract_patient_info(input_str, 'doctor_name')
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_doctor_name_from_query",
                "success": name_extracted['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not name_extracted['success']:
                return _build_response(
                    f'{name_extracted["value"]}, please tell the doctor name again.',
                    "get_appointment_slots",
                    {},
                    "in_progress",
                    # "appointment_slots_info",
                    step_metrics={
                        "subactions": subactions
                    }
                )

            # 2. Find best match
            db1_start = time.time()
            result = await find_best_match(name_extracted["value"])
            db1_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "find_best_match",
                "success": result['success'],
                "duration_ms": round((db1_end - db1_start) * 1000, 2),
            })

            if not result['success']:
                return _build_response(
                    'No doctor found with provided name. Please tell again ',
                    "get_appointment_slots",
                    {},
                    "in_progress",
                    # "appointment_slots_info",
                    step_metrics={
                        "subactions": subactions
                    }
                )

            doctor_name = result["name"]
            doctor_id = result["doctor_id"]

            # 3. Get available slots
            db2_start = time.time()
            slots_result = await get_available_slots(doctor_id)
            db2_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "get_available_slots",
                "success": slots_result.get("success", False),
                "duration_ms": round((db2_end - db2_start) * 1000, 2),
            })

            if not slots_result.get("success"):
                return _build_response(
                    f"No slots available for Doctor {doctor_name}.",
                    "get_appointment_slots",
                    {},
                    "resolved",
                    # "appointment_slots_info",
                    step_metrics={
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                        "subactions": subactions
                    }
                )

            slot_str = "\n".join([f"{slot[0]} {slot[1]}" for slot in slots_result["value"]])

            formated_response= await extract_patient_info(slots_result['value'],'format_response')

            return _build_response(
                f'Available slots for Doctor {doctor_name} are at {formated_response["value"]}',
                "get_appointment_slots",
                {"slots": slots_result["value"]},
                "resolved",
                # "appointment_slots_info",
                step_metrics={
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                    "subactions": subactions
                }
            )

        except Exception as e:
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_get_appointment_slots",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2),
            })

            logger.exception("Error while fetching appointment slots.")
            return _build_response(
                f"An error occurred: {str(e)} Please tell the doctor name again.",
                "get_appointment_slots",
                {},
                "error",
                # "appointment_slots_info",
                step_metrics={
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                    "subactions": subactions
                }
            )
