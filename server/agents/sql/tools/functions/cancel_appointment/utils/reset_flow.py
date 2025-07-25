from agents.sql.tools.functions.cancel_appointment.extract_appointment_details import extract_appointment_details
# from agents.sql.tools.functions.cancel_appointment.validate_appointment_details import validate_appointment_details
from agents.sql.tools.functions.cancel_appointment.delete_appointment_record import delete_appointment_record
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.functions.cancel_appointment.core.handle_appointment_id_step import handle_appointment_id_step
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

def reset_flow(message: str,collected_data:Dict , current_step :Dict) -> Dict:
        """Reset the cancellation flow"""
        current_step = 'get_appointment_id'
        collected_data = {}
        return _build_response(
            message,    
            'get_appointment_id',
            {},
            status='in_progress'
            
        )       
        