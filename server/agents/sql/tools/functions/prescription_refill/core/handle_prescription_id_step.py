from agents.sql.tools.functions.prescription_refill.extract_prescription_details import extract_prescription_details
from agents.sql.tools.functions.prescription_refill.update_prescription_record import update_prescription_record
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.functions._build_response import _build_response

from langchain.tools import StructuredTool
from typing import Dict, Any, Optional, Union
import json
import logging
import asyncio
import re
import time

logger = logging.getLogger(__name__)
async def handle_prescription_id_step(input_str: str,collected_data:Dict) -> Dict:
        step_start_time = time.time()
        subactions = []

        try:
            input_str = str(input_str).strip()
            if not input_str:
                return _build_response(
                    "Please provide your prescription ID.", 
                    'get_prescription_id',
                    collected_data,
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Extract prescription ID
            llm_start = time.time()
            extracted_id = await extract_patient_info(input_str, 'prescription_id')
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_prescription_id",
                "reason": extracted_id["value"],
                "success": extracted_id['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not extracted_id['success']:
                return _build_response(
                    "Please provide your prescription ID.", 
                    'get_prescription_id',
                    collected_data,
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            
            # Get prescription details
            db_start = time.time()
            details_result = await extract_prescription_details(extracted_id['value'])
            db_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "extract_prescription_details",
                "success": details_result['success'],
                "reason": details_result['value'],
                "duration_ms": round((db_end - db_start) * 1000, 2)
            })

            if not details_result['success'] and not details_result['refills_remaining']:
                return _build_response(
                    'No refills left. Please visit hospital', 
                    '', 
                    '', 
                    'resolved',
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            if not details_result['success']:
                logger.warning(f"No prescription id found in record. Give correct prescription id please: {input_str}")
                return _build_response(
                    f"{details_result['value']}, please tell again your prescription ID.",
                    'get_prescription_id',
                    collected_data,
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            
            # Store all relevant details from the response in session
            collected_data.update({
                "prescription_id": details_result["prescription_id"],
                "patient_id": details_result["patient_id"],
                "patient_name": details_result["patient_name"],
                "doctor_name": details_result["doctor_name"],
                "medication_name": details_result["medication_name"],
                "dosage": details_result["dosage"],
                "refills_allowed": details_result["refills_allowed"],
                "refills_remaining": details_result["refills_remaining"]
            })

            confirmation_prompt = (
                f"{details_result['value']}"
                ". Do you want to proceed with refilling this prescription (yes/no)"
            )

            # formated_resonse = await extract_patient_info(confirmation_prompt, 'format_response')

            return _build_response(
                confirmation_prompt, 
                'confirm_refill',
                collected_data,
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Error in prescription ID step: {str(e)}", exc_info=True)
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_prescription_id_step",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred while processing your request. Please tell again your prescription ID.",
                'get_prescription_id',
                status='error',
                
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )