from agents.sql.tools.functions.book_appointment.create_appointment_record import create_appointment_record
from agents.sql.tools.functions.book_appointment.extract_patient_details import extract_patient_details
from agents.sql.tools.functions.appointmentSlots_info.get_available_slots import get_available_slots    
from langchain.tools import StructuredTool
from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info
from agents.sql.tools.register_patient import run_register_patient
from agents.sql.tools.functions.find_best_match import find_best_match
from agents.sql.tools.functions.book_appointment.core.handle_reason_step import handle_reason_step
from agents.sql.tools.functions.book_appointment.core.handle_doctor_step import  handle_doctor_step
from agents.sql.tools.functions.book_appointment.core.handle_time_step import  handle_time_step
from agents.sql.tools.functions.book_appointment.core.handle_assure_registration import handle_assure_registration
from agents.sql.tools.functions.book_appointment.core.handle_registering_step import  handle_registering_step
from agents.sql.tools.functions.book_appointment.core.handle_confirm_step import  handle_confirm_step
from agents.sql.tools.functions.book_appointment.utils.normalize_input import  normalize_input
from typing import Dict, Any
from typing import Union 
import logging
import asyncio
import json

from agents.sql.tools.functions._build_response import _build_response
import time

logger = logging.getLogger(__name__)

class AppointmentBookingTool:
    def __init__(self):
        self.current_step = "get_doctor"
        self.collected_data = {}

    async def invoke(self, input_data: Any, context: Dict = None) -> Dict:
        """Main entry point with complete type safety"""
        try:
            # Debug what we received
            logger.debug(f"Raw input: {input_data} (type: {type(input_data)})")

            # Convert to safe format
            safe_input = normalize_input(input_data)
            
            # Extract values with guarantees
            query = str(safe_input['query_text'])
            ctx = safe_input.get('context', {}) or (context if isinstance(context, dict) else {})
            
            logger.debug(f"Processing - query: '{query}', context keys: {list(ctx.keys())}")
            return await self.handle_query(query, ctx)
            
        except Exception as e:
            logger.error(f"Booking error: {str(e)}", exc_info=True)
            return {
                "output": "We encountered a booking system error. Please try again.",
                "status": "error",
                "current_step": "get_doctor"
            }
  
    async def handle_query(self, input_str: str, context: Dict[str, Any]) -> Dict:
        """Main query handler with state machine"""
        self.current_step = context.get("current_step", "get_doctor")
        self.collected_data = context.get("collected_data", {})
        
        try:
            if self.current_step == "get_doctor":
                return await handle_doctor_step(input_str,self.collected_data)
            elif self.current_step == "get_time":
                return await handle_time_step(input_str, self.collected_data)
            elif self.current_step == "get_reason":
                return await handle_reason_step(input_str, context, self.collected_data)
            elif self.current_step == "confirm_booking":
                return await handle_confirm_step(input_str, self.collected_data)
            elif self.current_step == "assure_registration":
                return await handle_assure_registration(input_str, self.collected_data)
            elif self.current_step == "registering":
                return await handle_registering_step(input_str,context,self.collected_data)

            
            else:
                raise ValueError(f"Unknown step: {self.current_step}")
                
        except Exception as e:
            logger.error(f"Step {self.current_step} error: {str(e)}")
            return {
                "output": f"System error in {self.current_step} step. Let's start over.",
                "current_step": "get_doctor",
                "status": "error"
            }
        
def run_book_appointment(input: Union[str, Dict[str, Any]]) -> str:
    """Sync wrapper for appointment booking tool"""
    try:
        # Handle both string and dict input
        if isinstance(input, str):
            try:
                input = json.loads(input)
            except json.JSONDecodeError:
                input = {"query_text": input, "context": {}}
        
        query_text = input.get("query_text", "")
        context = input.get("context", {})
                
        tool_decison_start_time = context.get("tool_decison_start_time", '')

        if tool_decison_start_time:
            decision_duration_ms = (time.time() - float(tool_decison_start_time)) * 1000
        else:
            decision_duration_ms = None

        result = asyncio.run(AppointmentBookingTool().invoke(query_text, context))
        
        result['decision_duration_ms'] = decision_duration_ms
        result['current_tool'] = "booking_appointment"
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in run_book_appointment: {str(e)}")
        return json.dumps({
            "output": f"Booking error: {str(e)}",
            "current_step": "get_doctor",
            "collected_data": {},
            "status": "error"
        })
    
book_appointment_tool = StructuredTool.from_function(
    func=run_book_appointment,
    name="book_appointment_tool",
    # description=(
    #     "Use this tool book an appointment."
    # ),
    description=(
        "CALL THIS TOOL ONLY IF:  "
        "User wants to book an appointment."
    ),
    # args_schema=AppointmentBookingInput,
    return_direct=True
)

__all__ = ["book_appointment_tool"]

# from typing import Dict, Any, Union
# import json
# from langchain.tools import StructuredTool

# def no_op_book_appointment(input: Union[str, Dict[str, Any]]) -> str:
#     """
#     TESTING-ONLY TOOL: Simulates appointment booking without real actions.
    
#     CALL THIS TOOL WHEN:
#     - User explicitly requests to "book", "schedule", or "make appointment"
#     - Contains keywords: "appointment", "schedule", "book a visit"
    
#     NEVER CALL FOR:
#     - Cancellations ("cancel my appointment")
#     - Availability checks ("when is Dr. available")
#     - Prescription requests ("refill my medication")
#     """
#     # Parse input (matching your original format)
#     if isinstance(input, str):
#         try:
#             input_data = json.loads(input)
#         except json.JSONDecodeError:
#             input_data = {"query_text": input, "context": {}}
#     else:
#         input_data = input
    
#     # Return success response with no actual booking
#     return json.dumps({
#         "output": "[TEST] Booking request received (no action taken)",
#         "status": "success",
#         "current_step": "complete",
#         "collected_data": {
#             "doctor": "TEST_DOCTOR",
#             "time": "TEST_TIME",
#             "reason": "TEST_REASON"
#         }
#     })

# # Testing-only tool instance
# book_appointment_tool = StructuredTool.from_function(
#     func=no_op_book_appointment,
#     name="test_book_appointment_tool",
#     description=(
#         "CALL THIS TOOL ONLY IF:  "
#         "User wants to book an appointment."
#     ),
#     return_direct=True
# )
# __all__ = ["book_appointment_tool"]
