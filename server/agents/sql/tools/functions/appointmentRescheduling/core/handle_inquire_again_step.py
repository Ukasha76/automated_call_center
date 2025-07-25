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

async def handle_inquire_again_step(input_str: str,collected_data:Dict) -> Dict:
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
                
            if result['value'] == "No":
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

                # Get appointment details
                db_start = time.time()
                details_result = await extract_appointment_details(extracted_id)
                db_end = time.time()
                
                subactions.append({
                    "action_type": "db",
                    "action_name": "extract_appointment_details",
                    "success": details_result['success'],
                    "reason": details_result['value'] if not details_result['success'] else None,
                    "duration_ms": round((db_end - db_start) * 1000, 2),
                })

                if not details_result['success']:
                    logger.warning(f"Failed to fetch appointment details for ID: {input_str}")
                    return _build_response(
                        details_result['value'],
                        'get_appointmnet_id',
                        collected_data,
                        'in_progress',
                        # "appointment_rescheduling",
                        step_metrics={
                            "subactions": subactions,
                            "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                        }
                    )
                
                collected_data.update({
                    'patient_id': details_result['patient_id'],
                    'doctor_id': details_result['doctor_id'],
                    'patient_name': details_result['patient_name'],
                    'doctor_name': details_result['doctor_name'],
                    'day': details_result['day'],
                    'time': details_result['time'],
                    'reason': details_result['reason']
                })

                # Get available slots
                db2_start = time.time()
                available_slots = await get_available_slots(collected_data['doctor_id'])
                db2_end = time.time()
                
                subactions.append({
                    "action_type": "db",
                    "action_name": "get_available_slots",
                    "success": available_slots['success'],
                    "reason": "No slots available" if not available_slots['success'] else None,
                    "duration_ms": round((db2_end - db2_start) * 1000, 2),
                })

                if not available_slots['success']:
                    return _build_response(
                        f"No available slots for Dr. {collected_data['doctor_name']}",
                        '',
                        {},
                        'resolved',
                        "appointment_rescheduling",
                        step_metrics={
                            "subactions": subactions,
                            "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                        }
                    )
                
                collected_data["available_slots"] = available_slots['value']
                slot_str = "\n".join([f"{slot[0]} {slot[1]}" for slot in available_slots['value']])

                return _build_response(
                    f"Available slots for Dr. {collected_data['doctor_name']}:\n{slot_str}",
                    'get_time',
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
                    "action_name": "exception_in_inquire_again_processing",
                    "success": False,
                    "reason": str(e),
                    "duration_ms": round((time.time() - step_start_time) * 1000, 2),
                })
                
                logger.error(f"Database error: {str(e)}")
                return _build_response(
                    "Sorry, I couldn't cancel your appointment. Please try again.",
                    'get_appointment_id',
                    {},
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
                "action_name": "exception_in_inquire_again_step",
                "success": False,
                "reason": str(e),
                "duration_ms": round((time.time() - step_start_time) * 1000, 2),
            })
            
            logger.error(f"Error in inquire again step: {str(e)}", exc_info=True)
            return _build_response(
                "An error occurred while processing your request. Please try again.",
                'get_appointment_id',
                {},
                'error',
                # "appointment_rescheduling",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )