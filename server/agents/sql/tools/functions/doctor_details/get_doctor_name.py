
from typing import Dict
import logging
from agents.sql.tools.functions.find_best_match import find_best_match

from agents.sql.tools.functions.create_prompt import create_prompt

logger = logging.getLogger(__name__)

async def get_doctor_name(text: str) -> Dict:
    """
    Check if user input refers to Dr. Angella Webb without using regex.
    
    Args:
        text (str): User input
        
    Returns:
        Dict: Result indicating if the input refers to Angella Webb
    """
    try:
        system_message = """You are a name extraction tool. Follow these rules:
        1. If input contains a clear human name, return JUST the name
        2. If unsure or no name found, return empty string
        3. Never add explanations
        4. Examples:
        - "John Smith" → "John Smith"
        - "My name is Alice" → "Alice"
        - "register patient" → "",
        -Appointment slots info -> ""
        """
        name_extracted =  create_prompt(
            system_message,
            text
        ).strip()
        # print(name_extracted)

        # normalized_text = text.strip()
        response =await find_best_match(name_extracted)
        name = response["name"]
        doctor_id = response["doctor_id"]
        if name:
            return {
                'success': True,
                'value': name,
                'doctor_id': doctor_id,
                'confidence': 0.95
            }
        else:
            return {
                'success': False,
                'value': f"Can you please mention the name of the doctor clearly?",
                'confidence': 0.4
            }
    except Exception as e:
        logger.error(f"Error processing doctor details: {str(e)}")
        return {
            'success': False,
            'value': f"An error occurred: {str(e)}",
            'confidence': 0.0
        }
