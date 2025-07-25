from typing import Dict
import logging
from ...tools.functions.find_best_match import find_best_match

logger = logging.getLogger(__name__)

async def get_doctor_name(text: str) -> Dict:
    """
    Check if user input refers to a doctor name.
    
    Args:
        text (str): User input
        
    Returns:
        Dict: Result indicating if a doctor name was found
    """
    try:
        normalized_text = text.strip()
        name = await find_best_match(normalized_text)

        if name:
            return {
                'success': True,
                'value': name,
                'confidence': 0.95
            }
        else:
            return {
                'success': False,
                'value': f"Doctor name not found or not mentioned clearly.",
                'confidence': 0.4
            }
    except Exception as e:
        logger.error(f"Error processing doctor details: {str(e)}")
        return {
            'success': False,
            'value': f"An error occurred: {str(e)}",
            'confidence': 0.0
        } 