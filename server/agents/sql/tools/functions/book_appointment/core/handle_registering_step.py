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
from agents.sql.tools.functions.book_appointment.utils.complete_booking import complete_booking
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json
import time

logger = logging.getLogger(__name__)
from agents.sql.tools.functions._build_response import _build_response

async def handle_registering_step(input_str: str, context: Dict[str, Any] , collected_data : Dict) -> Dict:
        """Handle patient registration sub-flow with proper response structure"""
        step_start_time = time.time()
        subactions = []

        try:
            # Execute registration tool
            tool_start = time.time()
            result = await run_register_patient(input_str, context)
            tool_end = time.time()

            subactions.append({
                "action_type": "tool",
                "action_name": "patient_registration",
                "success": result['status'] != 'error',
                "reason": result.get("output", "Registration attempt"),
                "duration_ms": round((tool_end - tool_start) * 1000, 2)
            })

            # Still in registration process
            if result["status"] == "in_progress":
                return _build_response(
                    result["output"],
                    'registering',
                    collected_data,
                    # 'in_progress',
                    # "booking_appointment",
                    step_metrics={
                        "subactions": subactions,
                        "step_duration_ms": round((time.time() - step_start_time) * 1000, 2),
                        "registration_substep": result["current_step"],
                        "registration_data": result["collected_data"]
                    }
                )
            
            # Registration completed successfully
            if result["status"] == "complete":
                collected_data["patient_id"] = result["output"]
                return await complete_booking(collected_data)

            # Registration failed
            return _build_response(
                result["output"],
                'registering',
                result.get("collected_data", context),
                'error',
                "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )

        except Exception as e:
            logger.error(f"Error in registration handling step: {str(e)}")
            subactions.append({
                "action_type": "error",
                "action_name": "exception_in_registration_step",
                "success": False,
                "duration_ms": round((time.time() - step_start_time) * 1000, 2)
            })

            return _build_response(
                "An error occurred during registration. lets register again.",
                'registering',
                collected_data,
                'error',
                "booking_appointment",
                step_metrics={
                    "subactions": subactions,
                    "step_duration_ms": round((time.time() - step_start_time) * 1000, 2)
                }
            )
    