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

async def handle_confirmation_step(input_str: str,collected_data:Dict) -> Dict:
        step_start_time = time.time()
        subactions = []

        try:
            # Extract confirmation response
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

            if not result['success']:
                return _build_response(
                    f"{result['value']}, please confirm if you want to refill your prescription.",
                    'confirm_refill',
                    collected_data,
                    status='error',
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            
            if result['value'].lower() == "no":
              return _build_response(
                    f"The prescription refill aborted successfully.",
                    None,
                    None,
                    'resolved',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )


            try:
                # Update prescription record
                db_start = time.time()
                result = await update_prescription_record(collected_data)
                db_end = time.time()

                subactions.append({
                    "action_type": "db",
                    "action_name": "update_prescription_record",
                    "success": result['success'],
                    "reason": result['value'],
                    "duration_ms": round((db_end - db_start) * 1000, 2)
                })

                if not result['success']:
                    return _build_response(
                        f"{result['value']}, please confirm if you want to refill your prescription.",
                        'get_prescription_id', 
                        status='error',
                        step_metrics={
                            "subactions": subactions,
                            "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                        }
                    )
                confirmation_msg= "Your prescription has been successfully refilled. Your refill id is {result['refill_id']} valid until {result['valid_until']}",


                # formated_response= await extract_patient_info(confirmation_msg,'format_response')

                return _build_response(
                    f"Your prescription has been successfully refilled! Your refill id is {result['refill_id']} valid until {result['valid_until']}",
                    '',
                    'None',
                    status='resolved',
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                subactions.append({
                    "action_type": "error",
                    "action_name": "exception_in_prescription_update",
                    "success": False,
                    "duration_ms": round((time.time() - step_start_time) * 1000, 2)
                })

                return _build_response(
                    "Sorry, I couldn't refill your prescription. Please try again.",
                    'get_prescription_id',
                    status='error',
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
                "An error occurred while processing your confirmation. Please tell again if you want to refill your prescription.(yes/no)",
                'confirm_refill',
                status='error',
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

    