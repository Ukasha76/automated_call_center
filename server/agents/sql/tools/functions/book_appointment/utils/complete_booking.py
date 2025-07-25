# appointment_steps/reason_handler.py

import time
from typing import Dict
from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
from agents.sql.tools.functions.book_appointment.extract_patient_details import extract_patient_details
from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
from langchain.tools import StructuredTool
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.register_patient import run_register_patient
from agents.sql.tools.functions.find_best_match import find_best_match
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)
from agents.sql.tools.functions._build_response import _build_response

async def complete_booking(context: Dict) -> Dict:
        """Finalize appointment booking with proper metrics and error handling"""
        step_start_time = time.time()
        subactions = []

        try:
            booking_data = {
                "doctor_id": context["doctor_id"],
                "patient_id": context["patient_id"],
                "reason": context["reason"],
                "selected_time": context["selected_time"]
            }
            
            # Create booking record
            db_start = time.time()
            booking_result = await create_appointment_record(booking_data)
            db_end = time.time()

            subactions.append({
                "action_type": "db",
                "action_name": "create_appointment",
                "success": booking_result.get("success", False),
                "reason": booking_result.get("message", "Appointment creation"),
                "duration_ms": round((db_end - db_start) * 1000, 2)
            })

            if booking_result.get("success"):
                appointment_id = booking_result['value'].data[0]['appointment_id']
                success_msg = (
                    f"Success! Your appointment with Dr. {context['doctor']} "
                    f"at {context['selected_time']} is confirmed. "
                    f"Appointment ID: {appointment_id}"
                )
                
                return _build_response(
                    success_msg,
                    None,
                    {},
                    'resolved',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                    }
                )
            
            return _build_response(
                f"Booking failed: {booking_result.get('value', 'Unknown error')}",
                'confirm_booking',
                context,
                'error',
                # "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Booking completion error: {str(e)}")
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_booking_completion",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "System error during booking",
                'confirm_booking',
                context,
                'error',
                # "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )