# from typing import Dict

# def _build_response(message: str, next_step: str = None, collected_data: dict ={}, status: str = 'in_progress', current_tool:str = None) -> Dict:
#     """Helper to build consistent response structure"""
#     return {
#         'output': message,
#         'current_step': next_step,
#         'collected_data': collected_data,
#         'status': status,
#         'current_tool':current_tool
#         # 'decision_duration_ms':decision_duration_ms
#     }

# __all__ = ["_build_response"]  # Add this to your existing __all__ list
from typing import Dict

def _build_response(
    message: str,
    next_step: str = None,
    collected_data: dict = {},
    status: str = 'in_progress',
    current_tool: str = None,
    step_metrics: dict = None
) -> Dict:
    """Helper to build consistent response structure"""
    response = {
        'output': message,
        'current_step': next_step,
        'collected_data': collected_data,
        'status': status,
        'current_tool': current_tool
    }

    if step_metrics:
        response['step_metrics'] = step_metrics

    return response

__all__ = ["_build_response"]
