# from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
# from agents.sql.tools.functions.book_appointment.extract_patient_details import extract_patient_details
# from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
# from langchain.tools import StructuredTool
# from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
# # from agents.sql.tools.register_patient import run_register_patient
# from agents.sql.tools.functions.find_best_match import find_best_match
# from agents.sql.tools.functions.book_appointment.core.handle_reason_step import handle_reason_step
# from agents.sql.tools.functions.book_appointment.core.handle_doctor_step import  handle_doctor_step
# from agents.sql.tools.functions.book_appointment.core.handle_time_step import  handle_time_step
# from agents.sql.tools.functions.book_appointment.core.handle_assure_registration import handle_assure_registration
# from agents.sql.tools.functions.book_appointment.core.handle_registering_step import  handle_registering_step
# from agents.sql.tools.functions.book_appointment.core.handle_confirm_step import  handle_confirm_step
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json

# from agents.sql.tools.functions._build_response import _build_response
import time

logger = logging.getLogger(__name__)

def normalize_input(input_data: Any) -> Dict[str, Any]:
        """More robust input normalization"""
        normalized = {"query_text": "", "context": {}}
        
        if isinstance(input_data, dict):
            normalized["query_text"] = str(input_data.get("query_text", input_data.get("input", "")))
            if "context" in input_data:
                normalized["context"] = input_data["context"] if isinstance(input_data["context"], dict) else {}
        elif isinstance(input_data, str):
            try:
                parsed = json.loads(input_data)
                if isinstance(parsed, dict):
                    return normalize_input(parsed)
                normalized["query_text"] = str(parsed)
            except json.JSONDecodeError:
                normalized["query_text"] = input_data
        else:
            normalized["query_text"] = str(input_data)
            
        return normalized