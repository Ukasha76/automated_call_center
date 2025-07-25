from agents.sql.tools.functions.cancel_appointment.extract_appointment_details import extract_appointment_details
# from agents.sql.tools.functions.cancel_appointment.validate_appointment_details import validate_appointment_details
from agents.sql.tools.functions.cancel_appointment.delete_appointment_record import delete_appointment_record
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from langchain.tools import Tool
from typing import Dict, Any
import logging
from agents.sql.tools.functions._build_response import _build_response
from agents.sql.tools.functions.cancel_appointment.utils.reset_flow import reset_flow
from langchain.tools import StructuredTool
import random
import string
import logging
import asyncio
import re
import json
import time
from typing import Optional, Tuple

from typing import Union  
logger = logging.getLogger(__name__)
async def handle_confirmation_step(input_str: str, collected_data:Dict) -> Dict:
        """Handle confirmation step"""
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
                    f"{result['value']}, please confirm if you want to cancel your appointment.(yes/no)",
                    'confirm_rescheduling',
                    collected_data,
                    'error',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            
            if result['value'].lower() == "no":
                return _build_response(
                    f"The appointment cancelling procedure aborted successfully.",
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
                # Cancel appointment
                db_start = time.time()
                result = await delete_appointment_record(collected_data['appointment_id'])
                db_end = time.time()

                subactions.append({
                    "action_type": "db",
                    "action_name": "delete_appointment",
                    "success": result['success'],
                    "reason": result['value'],
                    "duration_ms": round((db_end - db_start) * 1000, 2)
                })

                if not result['success']:
                    return _build_response(
                        f"{result['value']}, please tell your appointment ID again.",
                        'get_appointmnet_id',
                        {},
                        'error',
                        # "cancel_appointment",
                        step_metrics={
                            "subactions": subactions,
                            "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                        }
                    )
                
                return _build_response(
                    f"Your appointment has been successfully canceled",
                    None,
                    None,
                    'resolved',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )       

            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                subactions.append({
                    "action_type": "error",
                    "action_name": "exception_in_appointment_cancellation",
                    "success": False,
                    "duration_ms": round((time.time() - step_start_time) * 1000, 2)
                })

                return _build_response(
                    "Sorry, I can not cancel your appointment. please tell your appointment ID again.",
                    'get_appointment_id',
                    {},
                    'error',
                    # "cancel_appointment",
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
                "An error occurred while processing your confirmation. Please tell again are your sure you want to cancel your appointment?",
                'confirm_cancellation',
                collected_data,
                'error',
                # "cancel_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
