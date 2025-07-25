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
async def handle_appointment_id_step(input_str: str, collected_data: Dict) -> Dict:
    """Handle appointment ID input step with validation and error handling."""
    step_start_time = time.time()
    subactions = []
    
    try:
        # Clean and validate input
        input_str = str(input_str).strip() if input_str else ""
        
        # Handle empty input case
        if not input_str:
            return _build_response(
                "Please provide your appointment ID.",
                'get_appointment_id',
                collected_data,
                'in_progress',
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
        
        # Process appointment ID extraction
        llm_start = time.time()
        extracted_id = await extract_patient_info(input_str, 'appointment_id')
        subactions.append({
            "action_type": "llm",
            "action_name": "extract_appointment_id",
            "success": extracted_id['success'],
            "reason": extracted_id['value'] if not extracted_id['success'] else None,
            "duration_ms": round((time.time() - llm_start) * 1000, 2),
        })

        if not extracted_id['success']:
            return _build_response(
                "Please provide your appointment ID.",
                'get_appointment_id',
                collected_data,
                'in_progress',
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        collected_data['appointment_id'] = extracted_id['value']
        appointment_id = collected_data['appointment_id']
        
        # Process appointment details
        db_start = time.time()
        details_result = await extract_appointment_details(appointment_id)
        subactions.append({
            "action_type": "db",
            "action_name": "extract_appointment_details",
            "success": details_result['success'],
            "reason": details_result['value'] if not details_result['success'] else None,
            "duration_ms": round((time.time() - db_start) * 1000, 2),
        })

        if not details_result['success']:
            logger.warning(f"Failed to fetch appointment details for ID: {input_str}")
            return _build_response(
                f"{details_result['value']}, Please provide your appointment ID again.",
                'get_appointment_id',
                collected_data,
                'in_progress',
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
        
        # Update collected data with appointment details
        collected_data.update({
            'patient_id': details_result['patient_id'],
            'doctor_id': details_result['doctor_id'],
            'patient_name': details_result['patient_name'],
            'doctor_name': details_result['doctor_name'],
            'day': details_result['day'],
            'time': details_result['time'],
            'reason': details_result['reason']
        })

        # Process available slots
        db2_start = time.time()
        available_slots = await get_available_slots(collected_data['doctor_id'])
        subactions.append({
            "action_type": "db",
            "action_name": "get_available_slots",
            "success": available_slots['success'],
            "reason": "No slots available" if not available_slots['success'] else None,
            "duration_ms": round((time.time() - db2_start) * 1000, 2),
        })

        if not available_slots['success']:
            return _build_response(
                f"No available slots for Doctor {collected_data['doctor_name']}",
                '',
                {},
                'resolved',
                "appointment_rescheduling",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
        
        # Format and return available slots
        collected_data["available_slots"] = available_slots['value']
        slot_str = "\n".join([f"{slot[0]} {slot[1]}" for slot in available_slots['value']])
        format_response = await extract_patient_info(slot_str, 'format_response')
        
        return _build_response(
            f"Available slots for Doctor {collected_data['doctor_name']} are {format_response['value']} . Please tell a time slot",
            'get_time',
            collected_data,
            'in_progress',
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
            "Sorry, we currently faced an error. Please tell your appointment id again.",
            'get_appointment_id',
            {},
            'error',
            step_metrics={
                "subactions": subactions,
                "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
            }
        )

# async def handle_appointment_id_step(input_str: str,collected_data:Dict) -> Dict:
#         """Handle appointment ID input step with validation and error handling."""
#         step_start_time = time.time()
#         subactions = []
        
#         try:
#             # Clean and validate input
#             input_str = str(input_str).strip() if input_str else ""
            
#             if not input_str:
#                 return _build_response(
#                     "Please provide your appointment ID.",
#                     'get_appointment_id',
#                     collected_data,
#                     'in_progress',
#                     # "appointment_rescheduling",
#                     step_metrics={
#                         "subactions": subactions,
#                         "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                     }
#                 )
                
#             # Extract appointment ID
#             llm_start = time.time()
#             extracted_id = await extract_patient_info(input_str, 'appointment_id')
#             llm_end = time.time()
            
#             subactions.append({
#                 "action_type": "llm",
#                 "action_name": "extract_appointment_id",
#                 "success": extracted_id['success'],
#                 "reason": extracted_id['value'] if not extracted_id['success'] else None,
#                 "duration_ms": round((llm_end - llm_start) * 1000, 2),
#             })

#             if not extracted_id['success']:
#                 return _build_response(
#                     f"Please provide your appointment ID.",
#                     'get_appointment_id',
#                     collected_data,
#                     'in_progress',
#                     # "appointment_rescheduling",
#                     step_metrics={
#                         "subactions": subactions,
#                         "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                     }
#                 )

#             collected_data.update({
#                 'appointment_id': extracted_id['value']
#             })

#             extracted_id = collected_data['appointment_id']
#                 # Get appointment details
#             db_start = time.time()
#             details_result = await extract_appointment_details(extracted_id)
#             db_end = time.time()
                
#                 subactions.append({
#                     "action_type": "db",
#                     "action_name": "extract_appointment_details",
#                     "success": details_result['success'],
#                     "reason": details_result['value'] if not details_result['success'] else None,
#                     "duration_ms": round((db_end - db_start) * 1000, 2),
#                 })

#                 if not details_result['success']:
#                     logger.warning(f"Failed to fetch appointment details for ID: {input_str}")
#                     return _build_response(
#                         details_result['value'],
#                         'get_appointmnet_id',
#                         collected_data,
#                         'in_progress',
#                         # "appointment_rescheduling",
#                         step_metrics={
#                             "subactions": subactions,
#                             "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                         }
#                     )
                
#                 collected_data.update({
#                     'patient_id': details_result['patient_id'],
#                     'doctor_id': details_result['doctor_id'],
#                     'patient_name': details_result['patient_name'],
#                     'doctor_name': details_result['doctor_name'],
#                     'day': details_result['day'],
#                     'time': details_result['time'],
#                     'reason': details_result['reason']
#                 })

#                 # Get available slots
#                 db2_start = time.time()
#                 available_slots = await get_available_slots(collected_data['doctor_id'])
#                 db2_end = time.time()
                
#                 subactions.append({
#                     "action_type": "db",
#                     "action_name": "get_available_slots",
#                     "success": available_slots['success'],
#                     "reason": "No slots available" if not available_slots['success'] else None,
#                     "duration_ms": round((db2_end - db2_start) * 1000, 2),
#                 })

#                 if not available_slots['success']:
#                     return _build_response(
#                         f"No available slots for Dr. {collected_data['doctor_name']}",
#                         '',
#                         {},
#                         'resolved',
#                         "appointment_rescheduling",
#                         step_metrics={
#                             "subactions": subactions,
#                             "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                         }
#                     )
                
#                 collected_data["available_slots"] = available_slots['value']
#                 slot_str = "\n".join([f"{slot[0]} {slot[1]}" for slot in available_slots['value']])
#                 format_response = await extract_patient_info(slot_str,'format_response')
#                 return _build_response(
#                     f"Available slots for Dr. {collected_data['doctor_name']} are {format_response['value']}",
#                     'get_time',
#                     collected_data,
#                     'in_progress',
#                     # "appointment_rescheduling",
#                     step_metrics={
#                         "subactions": subactions,
#                         "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                     }
#                 )

#         except Exception as e:
#                 subactions.append({
#                     "action_type": "error",
#                     "action_name": "exception_in_inquire_again_processing",
#                     "success": False,
#                     "reason": str(e),
#                     "duration_ms": round((time.time() - step_start_time) * 1000, 2),
#                 })
                
#                 logger.error(f"Database error: {str(e)}")
#                 return _build_response(
#                     "Sorry, I couldn't cancel your appointment. Please try again.",
#                     'get_appointment_id',
#                     {},
#                     'error',
#                     # "appointment_rescheduling",
#                     step_metrics={
#                         "subactions": subactions,
#                         "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
#                     }
#                 )    