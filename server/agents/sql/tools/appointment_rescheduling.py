from agents.sql.tools.functions._build_response import _build_response
from agents.sql.tools.functions.appointmentRescheduling.core.handle_appointment_id_step import handle_appointment_id_step
from agents.sql.tools.functions.appointmentRescheduling.core.handle_confirmation_step import handle_confirmation_step
from agents.sql.tools.functions.appointmentRescheduling.core.handle_inquire_again_step import handle_inquire_again_step
from agents.sql.tools.functions.appointmentRescheduling.core.handle_time_step import handle_time_step
from agents.sql.tools.functions.book_appointment.utils.normalize_input import  normalize_input
from typing import Dict, Any
import logging
from langchain.tools import StructuredTool
import logging
import asyncio
import time
import json
from typing import Union  
logger = logging.getLogger(__name__)

class AppointmentReschedulingTool:
    def __init__(self):
        self.current_step = "get_appointment_id"
        self.collected_data = {}

    async def invoke(self, input_data: Any, context: Dict = None) -> Dict:
        """Main entry point that matches LangChain's expected interface"""
        try:
            safe_input = normalize_input(input_data)
            query = str(safe_input['query_text'])
            ctx = safe_input.get('context', {}) or (context if isinstance(context, dict) else {})
            
            
            return await self.handle_query(query, ctx)
        
        except Exception as e:
            logger.error(f"Invoke error: {str(e)}", exc_info=True)
            return {
                "output": f"System error: {str(e)}",
                "status": "error",
                "debug": {
                    "input_received": str(input_data)[:100],
                    "input_type": str(type(input_data))
                }
            }   

    async def handle_query(self, input_str: str, context: Dict[str, Any]) -> Dict:
        """
        Handles the appointment cancellation process.
        Returns dict with:
        - response: string for user
        - current_step: next step identifier
        - collected_data: updated context
        - status: 'in_progress'|'complete'|'error'
        """
        self.current_step = context.get('current_step', 'get_appointment_id')
        self.collected_data = context.get('collected_data', {})

        try:
            if self.current_step == 'get_appointment_id':
                return await handle_appointment_id_step(input_str,self.collected_data)
            # elif self.current_step == 'inquire_again':
            #     return await handle_inquire_again_step(input_str,self.collected_data)
            elif self.current_step == 'get_time':
                return await handle_time_step(input_str,context,self.collected_data)
            elif self.current_step == 'confirm_rescheduling':
                return await handle_confirmation_step(input_str,self.collected_data)
            
        except Exception as e:
            logger.error(f"Cancellation error: {str(e)}")
            return self._reset_flow("I encountered an error. Let's start over.")
      
    def _reset_flow(self, message: str) -> Dict:
        """Reset the cancellation flow"""
        self.current_step = 'get_appointment_id'
        self.collected_data = {}
        return _build_response(
            message,
            'get_appointment_id',
            {},
            status='in_progress'
            # "appointment_rescheduling" 
        )       
        

# Create tool instance
rescheduling_appointment = AppointmentReschedulingTool()


def run_rescheduling_appointment(input: Union[str, Dict[str, Any]]) -> str:
    try:
        # Handle both string and dict input
        if isinstance(input, str):
            try:
                input = json.loads(input)
            except json.JSONDecodeError:
                input = {"query_text": input, "context": {}}
        
        query_text = input.get("query_text", "")
        context = input.get("context", {})
        
        tool_decison_start_time = context.get("tool_decison_start_time",'')

        if tool_decison_start_time:
            decision_duration_ms = (time.time() - float(tool_decison_start_time)) * 1000
        else:
            decision_duration_ms = None

        result = asyncio.run(rescheduling_appointment.invoke(query_text, context))
        
        result['decision_duration_ms'] = decision_duration_ms

        result['current_tool']='appointment_rescheduling'

        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in run_register_patient: {str(e)}")
        return json.dumps({
            "output": f"Registration error: {str(e)}",
            "current_step": "",
            "collected_data": {},
            "status": "error"
        })
# LangChain tool decorator
rescheduling_appointment_tool = StructuredTool.from_function(
    func=run_rescheduling_appointment,
    name="Rescheduling Appointment",
    # description=(
    #     "Rescheduling Appointment based on Appointment_id"
    #     "Input should be a dictionary with 'query_text' and 'context' or a JSON string."
    # ),
    description = """
    CALL THIS TOOL ONLY IF:  
    User's query is about rescheduling appointment.   
    """,
    return_direct=True
)

__all__ = ["rescheduling_appointment_tool"]

# from typing import Dict, Any, Union
# import json
# from langchain.tools import StructuredTool
# import logging
# import random

# logger = logging.getLogger(__name__)

# def no_op_reschedule_appointment(input: Union[str, Dict[str, Any]]) -> str:
#     """
#     TESTING-ONLY TOOL: Simulates appointment rescheduling without real changes.
    
#     CALL THIS TOOL WHEN:
#     - User requests to "reschedule", "change time", "move appointment"
#     - Contains keywords: "different time", "new slot", "can't make it"
    
#     NEVER CALL FOR:
#     - New bookings ("book an appointment")
#     - Cancellations ("cancel my visit")
#     - General availability ("when is Dr. available")
#     """
#     # Parse input (matching your original format)
#     if isinstance(input, str):
#         try:
#             input_data = json.loads(input)
#         except json.JSONDecodeError:
#             input_data = {"query_text": input, "context": {}}
#     else:
#         input_data = input
    
#     # Generate mock response based on step
#     current_step = input_data.get("context", {}).get("current_step", "get_appointment_id")
    
#     mock_responses = {
#         "get_appointment_id": {
#             "output": "[TEST] Please confirm the appointment ID to reschedule",
#             "current_step": "get_time",
#             "status": "in_progress"
#         },
#         "get_time": {
#             "output": "[TEST] What new time would you prefer? (Mock slots: 10am, 2pm, 4pm)",
#             "current_step": "confirm_rescheduling",
#             "status": "in_progress"
#         },
#         "confirm_rescheduling": {
#             "output": "[TEST] Your appointment has been rescheduled (no real change)",
#             "current_step": "complete",
#             "status": "complete",
#             "new_time": random.choice(["10:00", "14:00", "16:00"])
#         }
#     }
    
#     response = mock_responses.get(current_step, {
#         "output": "[TEST] Rescheduling flow started",
#         "current_step": "get_appointment_id",
#         "status": "in_progress"
#     })
    
#     response.update({
#         "decision_duration_ms": 100,  # Mock processing time
#         "current_tool": "appointment_rescheduling"
#     })
    
#     return json.dumps(response)

# # Testing-only tool instance
# rescheduling_appointment_tool = StructuredTool.from_function(
#     func=no_op_reschedule_appointment,
#     name="test_appointment_rescheduling",
#     # description="""
#     # TESTING ONLY: Simulates appointment rescheduling.
#     # Use ONLY when user wants to:
#     # - Change existing appointment time
#     # - Move to different date/slot
    
#     # Keywords: reschedule, change time, move appointment
#     # """,
#     description=(
#         "CALL THIS TOOL ONLY IF:  "
#         "User's query is related to rescheduling appointment ."
#     ),
#     return_direct=True
# )

# __all__ = ["rescheduling_appointment_tool"]  # Replace with real tool in production