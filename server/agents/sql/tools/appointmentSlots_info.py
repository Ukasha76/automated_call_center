from agents.sql.tools.functions.appointmentSlots_info.core.get_appointmetn_slots import get_appointment_slots
from langchain.tools import StructuredTool
from typing import Dict, Any, Union
import asyncio
import logging
import json
import time
logger = logging.getLogger(__name__)


# Async function
async def appointment_slots_info(input_str: str, context: Dict = None) -> Dict:
    return await get_appointment_slots(input_str, context)

# Sync wrapper
def run_appointment_slots_info(input: Union[str, Dict[str, Any]]) -> str:
    try:
        if isinstance(input, str):
            try:
                input = json.loads(input)
            except json.JSONDecodeError:
                input = {"query_text": input, "context": {}}

        query_text = input.get("query_text", "")
        context = input.get("context", {})

        tool_decison_start_time = context.get("tool_decison_start_time", '')
        decision_duration_ms = (time.time() - float(tool_decison_start_time)) * 1000 if tool_decison_start_time else None

        result = asyncio.run(appointment_slots_info(query_text, context))
        result['decision_duration_ms'] = decision_duration_ms
        result['current_tool'] = 'appointment_slots_info'

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error in run_appointment_slots_info: {str(e)}")
        return json.dumps({
            "output": f"Appointment slot error: {str(e)} , Please tell again.",
            "current_step": "get_time",
            "collected_data": {},
            "status": "error"
        })

# LangChain tool
appointment_slotsInfo_tool = StructuredTool.from_function(
    func=run_appointment_slots_info,
    name="Appointment Slots Info",
    description=(
        "CALL THIS TOOL ONLY IF:  "
        "User's query is about getting information on availbility of appointment slots."
    ),
    return_direct=True
)

__all__ = ["appointment_slotsInfo_tool"]

    # description=(
    #     "Use this tool to get available appointment slots for a doctor. "
    #     "Extract only the doctor's name from the query. "
    #     "Input should be a dictionary with 'query_text' and optional 'context'.")

# from typing import Dict, Any, Union
# import json
# from langchain.tools import StructuredTool
# import logging

# logger = logging.getLogger(__name__)

# def no_op_slots_info(input: Union[str, Dict[str, Any]]) -> str:
#     """
#     TESTING-ONLY TOOL: Simulates slot availability checks without real queries.
    
#     CALL THIS TOOL WHEN:
#     - User asks about "availability", "slots", "openings", "when is [X] available"
#     - Contains keywords: "available", "schedule", "open slots"
    
#     NEVER CALL FOR:
#     - Actual bookings ("book me an appointment")
#     - Doctor information ("what's Dr. Smith's specialty")
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
    
#     # Return mock slots data
#     return json.dumps({
#         "output": "[TEST] Slot availability request received (no real query)",
#         "status": "success",
#         "available_slots": [
#             "2023-12-01 09:00",
#             "2023-12-01 10:30",
#             "2023-12-02 14:00"
#         ],
#         "current_tool": "appointment_slots_info"
#     })

# # Testing-only tool instance
# appointment_slotsInfo_tool = StructuredTool.from_function(
#     func=no_op_slots_info,
#     name="test_appointment_slots_info",
#     description=(
#         "CALL THIS TOOL ONLY IF:  "
#         "User's query is about getting information on availbility of appointment slots."
#     ),
#     return_direct=True
# )

# __all__ = ["appointment_slotsInfo_tool"]  # Replace with real tool in production