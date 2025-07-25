from agents.sql.tools.functions.doctor_details.core.get_doctor_info import get_doctor_info
from langchain.tools import StructuredTool
from typing import Dict, Any, Union
import asyncio
import json
import logging
import time

logger = logging.getLogger(__name__)

# Async function (no class)
async def doctor_info(name: str, context: Dict = None) -> Dict:
    return await get_doctor_info(name, context)

# Sync wrapper
def run_doctor_info(input: Union[str, Dict[str, Any]]) -> str:
    try:
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

        result = asyncio.run(doctor_info(query_text, context))

        result['decision_duration_ms'] = decision_duration_ms
        result['current_tool'] = 'doctor_details'

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error in run_doctor_info: {str(e)}")
        return json.dumps({
            "output": f"Doctor info error: {str(e)}",
            "current_step": "get_doctor",
            "collected_data": {},
            "status": "error"
        })

# LangChain tool
doctor_info_tool = StructuredTool.from_function(
    func=run_doctor_info,
    name="Doctor Info",
    description = """
    CALL THIS TOOL ONLY IF:  
    User's query is about getting information or details about  doctor.   
    """,
    return_direct=True
)

__all__ = ["doctor_info_tool"]

# from typing import Dict, Any, Union
# import json
# from langchain.tools import StructuredTool
# import logging
# import random

# logger = logging.getLogger(__name__)

# def no_op_doctor_info(input: Union[str, Dict[str, Any]]) -> str:
#     """
#     TESTING-ONLY TOOL: Simulates doctor info lookup without real queries.
    
#     CALL THIS TOOL WHEN:
#     - User asks about "doctor", "Dr.", "physician", "profile", "details"
#     - Contains keywords: "who is", "about dr.", "specialist info"
    
#     NEVER CALL FOR:
#     - Appointment scheduling ("book with Dr. Smith")
#     - Slot availability ("when is Dr. available")
#     - Prescription requests ("refill from Dr. Lee")
#     """
#     # Parse input (matching your original format)
#     if isinstance(input, str):
#         try:
#             input_data = json.loads(input)
#         except json.JSONDecodeError:
#             input_data = {"query_text": input, "context": {}}
#     else:
#         input_data = input
    
#     # Generate mock doctor data
#     mock_doctors = {
#         "smith": {
#             "name": "Dr. Jane Smith",
#             "specialty": "Cardiology",
#             "languages": ["English", "Spanish"],
#             "availability": "Mon-Wed"
#         },
#         "lee": {
#             "name": "Dr. Michael Lee",
#             "specialty": "Pediatrics",
#             "languages": ["English", "Mandarin"],
#             "availability": "Thu-Fri"
#         }
#     }
    
#     # Extract name (case-insensitive)
#     query = input_data.get("query_text", "").lower()
#     matched_doctor = None
    
#     for name, data in mock_doctors.items():
#         if name in query:
#             matched_doctor = data
#             break
    
#     # Return mock response
#     return json.dumps({
#         "output": "[TEST] Doctor info request processed",
#         "status": "success",
#         "doctor_info": matched_doctor or random.choice(list(mock_doctors.values())),
#         "current_tool": "doctor_details"
#     })

# # Testing-only tool instance
# doctor_info_tool = StructuredTool.from_function(
#     func=no_op_doctor_info,
#     name="test_doctor_info",
#     description = """
#     CALL THIS TOOL ONLY IF:  
#     User's query is about getting information or details about  doctor.   
#     """,
#     return_direct=True
# )

# __all__ = ["doctor_info_tool"]  # Replace with real tool in production