from agents.sql.tools.functions.cancel_appointment.extract_appointment_details import extract_appointment_details
# from agents.sql.tools.functions.cancel_appointment.validate_appointment_details import validate_appointment_details
from agents.sql.tools.functions.cancel_appointment.delete_appointment_record import delete_appointment_record
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from langchain.tools import Tool
from typing import Dict, Any
import logging
from agents.sql.tools.functions._build_response import _build_response

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

async def handle_appointment_id_step(input_str: str , collected_data:Dict) -> Dict:
        """Handle appointment ID input step with validation and error handling.
        
        Args:
            input_str: The user-provided appointment ID
            
        Returns:
            Dictionary with:
            - response: Message to display to user
            - current_step: Next step in workflow
            - collected_data: Updated context data
            - status: Current status of workflow
        """
        step_start_time = time.time()
        subactions = []

        try:
            # Clean and validate input
            input_str = str(input_str).strip() if input_str else ""
            
            if not input_str:
                return _build_response(
                    "Please provide your appointment IDE.",
                    'get_appointment_id',
                    collected_data,
                    'in_progress',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Extract appointment ID
            llm_start = time.time()
            extracted_id = await extract_patient_info(input_str, 'appointment_id')
            llm_end = time.time()

            subactions.append({
                "action_type": "llm",
                "action_name": "extract_appointment_id",
                "reason": extracted_id["value"],
                "success": extracted_id['success'],
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            # Validate appointment ID format if needed
            if not extracted_id['success']:
                return _build_response(
                    f"Please provide your appointment IDE.",
                    'get_appointment_id',
                    collected_data,
                    'in_progress',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Get appointment details
            db_start = time.time()
            details_result = await extract_appointment_details(extracted_id['value'])
            db_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "extract_appointment_details",
                "success": details_result['success'],
                "reason": details_result['value'],
                "duration_ms": round((db_end - db_start) * 1000, 2)
            })
            
            if not details_result['success']:
                logger.warning(f"Failed to fetch appointment details for ID: {input_str}")
                return _build_response(
                    f"{details_result['value']}. Please check your appointment ID and try again.",
                    'get_appointmnet_id',
                    collected_data,
                    'in_progress',
                    # "cancel_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )

            # Store data for confirmation step
            collected_data.update({
                'appointment_id': details_result["appointment_id"],
                'formatted_details': details_result['value']   # Store formatted string
            })

            # Build confirmation prompt
            confirmation_prompt = (
                f"{details_result['value']}"
                "Are you sure you want to cancel this appointment (yes/no)"
            )
            # format_response = await extract_patient_info(
            #     confirmation_prompt, 'format_response'
            # )
            return _build_response(
                confirmation_prompt,
                'confirm_cancellation',
                collected_data,
                'in_progress',
                # "cancel_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Error in appointment ID step: {str(e)}", exc_info=True)
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_appointment_id_step",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred while taking your appointment id. Please tell again your appointment ID.",
                'get_appointment_id',
                {},
                'error',
                # "cancel_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )