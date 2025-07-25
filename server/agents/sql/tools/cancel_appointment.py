from agents.sql.tools.functions.cancel_appointment.core.handle_appointment_id_step import handle_appointment_id_step
from agents.sql.tools.functions.cancel_appointment.core.handle_confirmation_step import handle_confirmation_step
from langchain.tools import Tool
from typing import Dict, Any
import logging
from agents.sql.tools.functions.book_appointment.utils.normalize_input import  normalize_input

from agents.sql.tools.functions._build_response import _build_response

from langchain.tools import StructuredTool

import logging
import asyncio

import json
import time


from typing import Union  
logger = logging.getLogger(__name__)


class AppointmentCancellationTool:
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
            elif self.current_step == 'confirm_cancellation':
                return await handle_confirmation_step(input_str,self.collected_data)
                
        except Exception as e:
            logger.error(f"Cancellation error: {str(e)}")
            return self._reset_flow("I encountered an error. Lets start over. What is your appointment ID?")

   

    def _reset_flow(self, message: str) -> Dict:
        """Reset the cancellation flow"""
        self.current_step = 'get_appointment_id'
        self.collected_data = {}
        return _build_response(
            message,
            'get_appointment_id',
            {},
            status='in_progress'
            
        )       
        

# Create tool instance
cancellation_tool = AppointmentCancellationTool()


def run_cancel_appointment(input: Union[str, Dict[str, Any]]) -> str:
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

        result = asyncio.run(cancellation_tool.invoke(query_text, context))
        
        
        result['decision_duration_ms'] = decision_duration_ms
        result['current_tool']="cancel_appointment"

        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in run_register_patient: {str(e)}")
        return json.dumps({
            "output": f"Registration error: {str(e)}",
            "current_step": "get_name",
            "collected_data": {},
            "status": "error"
        })
# LangChain tool decorator
cancel_appointment_tool = StructuredTool.from_function(
    func=run_cancel_appointment,
    name="Cancel Appointment",
    # description=(
    #     "Cancel a Patient Appointment based on Appointment_id"
    #     "Input should be a dictionary with 'query_text' and 'context' or a JSON string."
    # ),
    description=(
        "CALL THIS TOOL ONLY IF:  "
        "User's query is cancelling appointment."
    ),
    return_direct=True
)

__all__ = ["cancel_appointment_tool"]
