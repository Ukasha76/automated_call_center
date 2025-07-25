
from agents.sql.tools.functions.prescription_refill.core.handle_prescription_id_step import handle_prescription_id_step
from agents.sql.tools.functions.prescription_refill.core.handle_confirmation_step import handle_confirmation_step
from agents.sql.tools.functions.book_appointment.utils.normalize_input import  normalize_input
from agents.sql.tools.functions._build_response import _build_response

from langchain.tools import StructuredTool
from typing import Dict, Any, Optional, Union
import json
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

class PrescriptionRefillTool:
    def __init__(self):
        self.current_step = "get_prescription_id"
        self.collected_data = {}

    async def invoke(self, input_data: Any, context: Dict = None) -> Dict:
        try:
            safe_input =normalize_input(input_data)
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
        self.current_step = context.get('current_step', 'get_prescription_id')
        self.collected_data = context.get('collected_data', {})

        try:
            if self.current_step == 'get_prescription_id':
                return await handle_prescription_id_step(input_str,self.collected_data)
            elif self.current_step == 'confirm_refill':
                return await handle_confirmation_step(input_str,self.collected_data)
            
        except Exception as e:
            logger.error(f"Refill error: {str(e)}")
            return self._reset_flow("I encountered an error. Lets start over , What is your prescription ID?")
    

    def _reset_flow(self, message: str, step_metrics: Dict = None) -> Dict:
        self.current_step = 'get_prescription_id'
        self.collected_data = {}
        return _build_response(
            message, 
            'get_prescription_id', 
            status='in_progress',
            step_metrics=step_metrics
        )

# Create instance
refill_tool_instance = PrescriptionRefillTool()

def run_prescription_refill(input: Union[str, Dict[str, Any]]) -> str:
    try:
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

        result = asyncio.run(refill_tool_instance.invoke(query_text, context))

        result['decision_duration_ms'] = decision_duration_ms

        result['current_tool']='prescription_refill'

        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in run_prescription_refill: {str(e)}")
        return json.dumps({
            "output": f"Refill error: {str(e)}",
            "current_step": "get_prescription_id",
            "collected_data": {},
            "status": "error"
        })

# LangChain tool
prescription_refill_tool = StructuredTool.from_function(
    func=run_prescription_refill,
    name="Refill Prescription",
    description=(
        "Refill a Patient's Prescription based on prescription_id. "
        "Input should be a dictionary with 'query_text' and 'context' or a JSON string."
    ),
    return_direct=True
)

__all__ = ["prescription_refill_tool"]
# from typing import Dict, Any, Union
# import json
# from langchain.tools import StructuredTool
# import logging
# import random

# logger = logging.getLogger(__name__)

# def no_op_prescription_refill(input: Union[str, Dict[str, Any]]) -> str:
#     """
#     TESTING-ONLY TOOL: Simulates prescription refills without real changes.
    
#     CALL THIS TOOL WHEN:
#     - User requests to "refill", "renew", or "get more" of a prescription
#     - Contains keywords: "medication refill", "need more pills", "prescription renewal"
    
#     NEVER CALL FOR:
#     - New prescriptions ("I need a new prescription")
#     - Appointment booking ("schedule with Dr. Smith")
#     - General inquiries ("what's in my prescription")
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
#     current_step = input_data.get("context", {}).get("current_step", "get_prescription_id")
    
#     mock_responses = {
#         "get_prescription_id": {
#             "output": "[TEST] Please provide your prescription ID",
#             "current_step": "confirm_refill",
#             "status": "in_progress"
#         },
#         "confirm_refill": {
#             "output": "[TEST] Your prescription has been refilled (no real change)",
#             "current_step": "complete",
#             "status": "complete",
#             "refill_id": f"RX-{random.randint(1000,9999)}",
#             "estimated_ready": "tomorrow at 2pm"
#         }
#     }
    
#     response = mock_responses.get(current_step, {
#         "output": "[TEST] Refill flow started",
#         "current_step": "get_prescription_id",
#         "status": "in_progress"
#     })
    
#     response.update({
#         "decision_duration_ms": 75,  # Mock processing time
#         "current_tool": "prescription_refill"
#     })
    
#     return json.dumps(response)

# # Testing-only tool instance
# prescription_refill_tool = StructuredTool.from_function(
#     func=no_op_prescription_refill,
#     name="test_prescription_refill",
#     # description="""
#     # TESTING ONLY: Simulates prescription refills.
#     # Use ONLY when user wants to:
#     # - Refill existing medication
#     # - Renew current prescription
    
#     # Keywords: refill, renew, more medication, prescription again
#     # """,
#     description=(
#         "CALL THIS TOOL ONLY IF:  "
#         "User's query is related to prescription refill."
#     ),
#     return_direct=True
# )

# __all__ = ["prescription_refill_tool"]  # Replace with real tool in production