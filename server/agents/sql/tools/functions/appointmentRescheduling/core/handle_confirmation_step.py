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

async def handle_confirmation_step(input_str: str, collected_data:Dict) -> Dict:
        """Handle confirmation step"""
        step_start_time = time.time()
        subactions = []
        
        try:
            # Extract confirmation
            llm_start = time.time()
            result = await extract_patient_info(input_str, 'confirmation')
            llm_end = time.time()
            
            subactions.append({
                "action_type": "llm",
                "action_name": "extract_confirmation",
                "success": result['success'],
                "reason": result['value'] if not result['success'] else None,
                "duration_ms": round((llm_end - llm_start) * 1000, 2),
            })

            if not result['success']:
                return _build_response(
                    f"{result['value']}, please tell are you sure you want to reschedule your appointment? (yes/no)",
                    'confirm_rescheduling',
                    collected_data,
                    'error',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
                
            if result['value'].lower() == "no":
                return _build_response(
                    f"The appointment rescheduling procedure aborted successfully.",
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
                extracted_id = collected_data['appointment_id']

                # Delete old appointment
                db1_start = time.time()
                delete_result = await delete_appointment_record(collected_data['appointment_id'])
                db1_end = time.time()
                
                subactions.append({
                    "action_type": "db",
                    "action_name": "delete_appointment",
                    "success": delete_result['success'],
                    "reason": delete_result['value'] if not delete_result['success'] else None,
                    "duration_ms": round((db1_end - db1_start) * 1000, 2),
                })

                # Create new appointment
                db2_start = time.time()
                booking_result = await create_appointment_record({
                    "patient_id": collected_data['patient_id'],
                    "doctor_id": collected_data['doctor_id'],
                    "selected_time": collected_data['selected_time'],
                    "reason": collected_data['reason']
                })
                db2_end = time.time()
                
                subactions.append({
                    "action_type": "db",
                    "action_name": "create_appointment",
                    "success": booking_result['success'],
                    "reason": booking_result['value'] if not booking_result['success'] else None,
                    "duration_ms": round((db2_end - db2_start) * 1000, 2),
                })

                if not booking_result['success']:
                    return _build_response(
                        f"{booking_result['value']}, please tell again are you sure you want to reschedule your appointment? (yes/no)",
                        'confirm_rescheduling',
                        collected_data,
                        'error',
                        # "appointment_rescheduling",
                        step_metrics={
                            "subactions": subactions,
                            "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                        }
                    )
                
                appointment_id = booking_result.get('value').data[0]['appointment_id']
                
                return _build_response(
                    f"Your appointment has been successfully rescheduled! Your appointment id is {appointment_id}",
                    '',
                    {},
                    'resolved',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )       
            except Exception as e:
                subactions.append({
                    "action_type": "error",
                    "action_name": "exception_in_confirmation_processing",
                    "success": False,
                    "reason": str(e),
                    "duration_ms": round((time.time() - step_start_time) * 1000, 2),
                })
                
                logger.error(f"Error in confirmation step: {str(e)}", exc_info=True)
                return _build_response(
                    "An error occurred while processing your request. Please tell are you sure you want to reschedule your appointment? (yes/no)",
                    'confirm_rescheduling',
                    collected_data,
                    'error',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
                
        except Exception as e:
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_confirmation_step",
                "success": False,
                "reason": str(e),
                "duration_ms": round((time.time() - step_start_time) * 1000, 2),
            })
            
            logger.error(f"Error in confirmation step: {str(e)}", exc_info=True)
            return _build_response(
                    "An error occurred while processing your request. Please tell are you sure you want to reschedule your appointment? (yes/no)",
                    'confirm_rescheduling',
                    collected_data,
                    'error',
                    # "appointment_rescheduling",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )