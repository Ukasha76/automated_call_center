from agents.sql.tools.functions.cancel_appointment.extract_appointment_details import extract_appointment_details
from agents.sql.tools.functions.cancel_appointment.delete_appointment_record import delete_appointment_record
from langchain.tools import Tool
from agents.sql.tools.functions._build_response import _build_response

from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from typing import Dict, Any
import logging
from langchain.tools import StructuredTool
import random
import string
import logging
import asyncio
import re
import time
import json
from typing import Optional, Tuple

from typing import Union  
logger = logging.getLogger(__name__)
async def handle_time_step(input_str: str, context: Dict , collected_data:Dict) -> Dict:
        """Handle time selection step"""
        step_start_time = time.time()
        subactions = []
        
        try:
            if not input_str.strip():
                return _build_response(
                    "Please specify your preferred time from the available slots.",
                    'get_time',
                    collected_data,
                    'in_progress',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
        
            # Extract time
            llm_start = time.time()
            time_result = await extract_patient_info(input_str, 'appointment_time', collected_data["available_slots"])
            llm_end = time.time()
            
            subactions.append({
                "action_type": "llm",
                "action_name": "extract_appointment_time",
                "success": time_result['success'],
                "reason": time_result['value'] if not time_result['success'] else None,
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not time_result.get("success"):
                return _build_response(
                    f"Couldnot find appointment time  {time_result.get('value', 'Unknown error')} , please specify your preferred time from the available slots, the available slots are: {collected_data.get('available_slots', 'Unknown')}",
                    'get_time',
                    collected_data,
                    'in_progress',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
                
            collected_data["selected_time"] = time_result['value']

            return _build_response(
                f"Do you want an appointment with Doctor {context.get('collected_data').get('doctor_name')} "
                             f"at {context.get('collected_data').get('selected_time')}? (yes/no)",
                'confirm_rescheduling',
                collected_data,
                'in_progress',
                # "appointment_rescheduling",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )        
        except Exception as e:
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_time_step",
                "success": False,
                "reason": str(e),
                "duration_ms": round((time.time() - step_start_time) * 1000, 2),
            })
            
            logger.error(f"Error in time step: {str(e)}", exc_info=True)
            return _build_response(
                f"An error occurred while processing your request.Please specify your preferred time from the available slots , the available slots are: {collected_data.get('available_slots', 'Unknown')}",
                'get_time',
                collected_data,
                'error',
                # "appointment_rescheduling",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )