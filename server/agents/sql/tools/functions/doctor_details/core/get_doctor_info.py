import time
from typing import Dict
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.functions.find_best_match import find_best_match
from agents.sql.tools.functions.doctor_details.extract_doctor_details import extract_doctor_details
from agents.sql.tools.functions._build_response import _build_response

async def get_doctor_info(name: str, context: Dict = None) -> Dict:
    context = context or {}
    step_start_time = time.time()
    subactions = []

    try:
        # 1. Extract doctor name using LLM
        llm_start = time.time()
        name_extracted = await extract_patient_info(name, 'doctor_name')
        llm_end = time.time()

        subactions.append({
            "action_type": "llm",
            "action_name": "extract_doctor_name",
            "reason": name_extracted["value"],
            "success": name_extracted['success'],
            "duration_ms": round((llm_end - llm_start) * 1000, 2),
        })

        if not name_extracted['success']:
            return _build_response(
                f'{name_extracted["value"]}, please tell me the name of the doctor you are looking for.',
                "get_doctor",
                {},
                "in_progress",
                step_metrics={"subactions": subactions, "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)}
            )

        # 2. Find best DB match
        db1_start = time.time()
        result = await find_best_match(name_extracted['value'])
        db1_end = time.time()

        subactions.append({
            "action_type": "db",
            "action_name": "find_best_match",
            "success": result['success'],
            "reason": result['name'],
            "duration_ms": round((db1_end - db1_start) * 1000, 2)
        })

        if not result['success']:
            return _build_response(
                "No doctor found with provided name. Please tell again.",
                "get_doctor",
                {},
                "in_progress",
                step_metrics={"subactions": subactions, "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)}
            )

        # 3. Extract doctor details
        db2_start = time.time()
        raw_details = await extract_doctor_details(result['name'])
        db2_end = time.time()

        subactions.append({
            "action_type": "db",
            "action_name": "extract_doctor_details",
            "success": raw_details['success'],
            "reason": raw_details['value'],
            "duration_ms": round((db2_end - db2_start) * 1000, 2)
        })

        details = raw_details.get('value', {})


        spoken_text = (
            f"Here is the doctor information you requested. "
            f"Doctor {details.get('name', 'Name not available')} specializes in {details.get('specialization', 'a medical field')}. "
            f"They are part of the {details.get('department', 'unspecified department')} department. "
            f"You can reach them at extension {details.get('extension', 'not available')} "
            f"or by email at {details.get('email', 'no email available')}."
        )
        # formated_response= await extract_patient_info(spoken_text,'format_response')

        return _build_response(
            spoken_text,
            "get_doctor",
            {"doctor": details},
            "resolved",
            step_metrics={
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                "subactions": subactions
            }
        )

    except Exception as e:
        subactions.append({
            "action_type": "error",
            "action_name": "exception_in_get_doctor_info",
            "success": False,
            "duration_ms": round((time.time() - step_start_time) * 1000, 2)
        })

        return _build_response(
            f"Error: {str(e)} while retrieving doctor information. Please tell again the name of doctor.",
            "get_doctor",
            {},
            "error",
            step_metrics={
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                "subactions": subactions
            }
        )