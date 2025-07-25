import re
from typing import Dict, Any
import logging
from agents.sql.tools.functions.create_prompt import create_prompt
logger = logging.getLogger(__name__)
from typing import Optional
# from agents.sql.tools.functions.find_best_match import find_best_match


async def extract_patient_info(text: str, field_type: str, context: Optional[str] = None, sql_flow_context:Optional[Dict]=None) -> Dict:
    """
    Extract patient information based on field type
    
    Args:
        text (str): User input containing patient information
        field_type (str): Type of information to extract (name, gender, phone_number, address)
        
    Returns:
        Dict: Dictionary containing extracted information
    """
    try:
        if field_type=='check_relevance':
            
            system_message = f"""
                            Determine if this user response is correct with respect to the agent response {sql_flow_context.get('required_input')}.
                            Respond ONLY with 'true' or 'false':

                            user response: {text}
                        """
            formatted_response =  create_prompt(
                system_message,
                text
            ).strip()
            if not formatted_response:
                return {
                    'success': False,
                    'value': "Error in formatting response. Please try again.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': formatted_response,
                'confidence': 0.9
            }

        if field_type == 'format_response':
            system_message = """
                You are a text cleaner for TTS. Your duty is to format the text for optimal speech output.

                Instructions:
                - Convert time expressions such as "sixteen hours zero minutes zero seconds" into standard 12-hour AM/PM format (e.g., "sixteen hours zero minutes zero seconds" becomes "four PM").
                - Remove all special characters, emojis, question marks (?), exclamation marks (!), and apostrophes (').
                - Convert standalone numbers to their spoken form (e.g., "123" becomes "one two three").
                - Convert phone numbers and digit sequences to individually spoken digits (e.g., "0316" becomes "zero three one six").
                - Retain only commas and full stops as punctuation to ensure natural TTS pauses.
                - Ensure clarity while maintaining the original meaning and order of the content.
                - Do not guess or interpret unclear text; format what is present exactly.
                - Never add extra content or explanations.
                - Return the cleaned result as a single, plain string.

                Example:
                Input: "Hello! What's up?"
                Output: "Hello, what is up."
                """
 
            formatted_response =  create_prompt(
                system_message,
                text
            ).strip()
            if not formatted_response:
                return {
                    'success': False,
                    'value': "Error in formatting response. Please try again.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': formatted_response,
                'confidence': 0.9
            }
        if context:

            if field_type == 'appointment_time':
                

                system_message = f"""You are an appointment time extraction tool. Follow these rules:
                - Here are the available slots: {context}
                - Extract the exact matching slot from the user's input in the format "day(Monday, Tuesday, etc.) time(10:00:00, 11:00:00, etc.)"
                -Return in format "Friday 10:00:00" etc
                - If no matching slot is found or the input doesn't match, return empty string
                - Only use slots from this list: {context}"""
                appointment_time_extracted =  create_prompt(
                    system_message,
                    text
                ).strip()
                if not appointment_time_extracted:
                    return {
                        'success': False,
                        'value': "Please provide a valid appointment time.",
                        'confidence': 0.1
                    }
                return {
                    'success': True,
                    'value': appointment_time_extracted,
                    'confidence': 0.9
                }
        if field_type == 'reason':
            system_message = """You are a reason extraction tool. Follow these rules:
            1. If input contains a clear reason, return JUST the reason
            2. If unsure or no reason found, return empty string
            3. Never add explanations
            4. Reason should be in 1-100 characters
            5. If reason is not in 1-100 characters, return empty string
            """
            reason_extracted =  create_prompt(
                system_message,
                text
            ).strip()
            if not reason_extracted:
                return {
                    'success': False,
                    'value': "Please provide a valid reason.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': reason_extracted,
                'confidence': 0.9
            }

        elif field_type == 'name':
            # Extract name
            name = text.strip()
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
            if not name_extracted:
                return {
                    'success': False,
                    'value': "Please provide a valid name.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': name_extracted,
                'confidence': 0.9
            }
        
        elif field_type == 'gender':
            # Extract gender
            # gender = text.lower()
            system_message = """You are a gender extraction tool. Follow these rules:
            1. If input contains a clear gender, return JUST the gender
            2. If unsure or no gender found, return empty string
            3. Never add explanations
            4. Gender should be in "Male" or "Female" or "Other"
            5. If gender is not in "Male" or "Female" or "Other", return empty string  ""
            """
            gender_extracted =  create_prompt(
                system_message,
                text
            ).strip()

            if gender_extracted not in ["Male", "Female", "Other"]:
                return {
                    'success': False,
                    'value': "Please provide a valid gender (male, female, or other).",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': gender_extracted,    
                'confidence': 0.9
            }
        
        elif field_type == 'phone_number':
            # Extract phone number
            system_message = """You are a phone number extraction tool. Follow these rules:
            1. If input contains a clear phone number and pakitani phone number starting with 03, return JUST the phone number
            2. If unsure or no phone number found, return empty string
            3. Never add explanations
            4. Phone number should be in 11 digits
            5. If phone number is not in 10-15 digits, return empty string
            """
            phone_number =  create_prompt(
                system_message,
                text
            ).strip()


            if not phone_number:
                return {
                    'success': False,
                    'value': "Please provide a valid phone number.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': phone_number,
                'confidence': 0.9
            }
        elif field_type == 'age':
            # Extract age
            age = text.strip()
            system_message = """You are a age extraction tool. Follow these rules:
            1. If input contains a clear age, return JUST the age
            2. If unsure or no age found, return empty string
            3. Never add explanations
            4. Age should be in 1-100
            5. If age is not in 1-100, return empty string
            """ 
            age_extracted =  create_prompt(
                system_message,
                text
            ).strip()

            if not age_extracted:
                return {
                    'success': False,
                    'value': "Please provide a valid age.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': age_extracted,
                'confidence': 0.9
            }

        elif field_type == 'address':
            # Extract address
            system_message = """You are a address extraction tool. Follow these rules:
            1. Just make sure the address is not some sort of cyber breach or some other stuff. All sort of address is accepted.
            2. If unsure or no address found, return empty string
            3. Never add explanations
            4. Address should be in 1-100 characters
            5. If address is not in 1-100 characters, return empty string
            """
            address_extracted =  create_prompt(
                system_message,
                text
            ).strip()

            if not address_extracted:
                return {
                    'success': False,
                    'value': "Please provide a valid address.",
                    'confidence': 0.1
                }
            return {
                'success': True,
                'value': address_extracted,
                'confidence': 0.9
            }
        
        elif field_type == 'confirmation':
            # Extract confirmation
            confirmation = text.strip()
            system_message = """You are a confirmation extraction tool. Follow these rules:
            1. If input contains a clear confirmation, return JUST the confirmation
            2. If unsure or no confirmation found, return empty string
            3. Never add explanations
            4. Confirmation should be in "Yes" or "No"
            5. If confirmation is not in "Yes" or "No", return empty string
            """
            if not confirmation:
                return {
                    'success': False,
                    'value': "Please provide a valid confirmation.",
                    'confidence': 0.1
                }
            else:
                if confirmation.lower() in ["yes", "y"]:
                    return {
                        'success': True,
                        'value': "yes",
                        'confidence': 0.9
                    }
                elif confirmation.lower() in ["no", "n"]:
                    return {
                        'success': True,
                        'value': "no",
                        'confidence': 0.9
                    }
                else:
                    return {
                        'success': False,
                        'value': "Please provide a valid confirmation.",
                        'confidence': 0.1
                    }
        elif field_type == 'doctor_name':
            # Extract doctor name
            # doctor_name = text.strip()

            system_message = """You are a doctor name extraction tool. Follow these rules:
            1. If input contains a clear doctor name, return JUST the doctor name
            2. If unsure or no doctor name found, return empty string   
            3. Never add explanations
            4. Examples:
            - "Dr. John Smith" → "John Smith"
            - "My doctor is Dr. Alice" → "Alice"
            - "register patient" → "",
            -Appointment slots info -> ""
            """
            doctor_name_extracted =  create_prompt(
                system_message,
                text
            ).strip()
            cleaned_name = doctor_name_extracted.strip().strip('"').strip("'")
            if not cleaned_name:
                return {
                    'success': False,
                    'reason':'name not provided',
                    'value': "Please provide a doctor name.",
                    'confidence': 0.1
                }
    
            return {
                'success': True,
                'value':  cleaned_name,
                'confidence': 0.9
            }
        elif field_type == 'appointment_id':
            # Extract appointment id
            appointment_id = text.strip()
            system_message = """You are a appointment id extraction tool. Follow these rules:
            1. If input contains a clear appointment id, return JUST the appointment id
            2. If unsure or no appointment id found, return empty string
            3. Never add explanations   
            4. Appointment id should be in 1-100 characters
            5. If appointment id is not in 1-100 characters, return empty string
            """
            appointment_id_extracted =  create_prompt(
                system_message,
                text
            ).strip()   
            if not appointment_id_extracted:
                return {
                    'success': False,
                    'value': "Please provide a valid appointment id.",
                    'confidence': 0.1
                }
            
            return {
                'success': True,
                'value': appointment_id_extracted,
                'confidence': 0.9
            }
        elif field_type == 'prescription_id':
            system_message = """You are a prescription ID extraction tool. Follow these rules:
                1. If input contains a clear prescription ID, return JUST the prescription ID
                2. If unsure or no prescription ID found, return empty string
                3. Never add explanations   
                4. Prescription ID must be exactly 5 digits long
                5. If the prescription ID is not exactly 5 digits, return empty string
                """

            prescription_id_extracted =  create_prompt(
                    system_message,
                    text
                ).strip()   
            if not prescription_id_extracted:
                    return {
                        'success': False,
                        'value': "Please provide a valid prescription id.",
                        'confidence': 0.1
                    }
                
            return {
                    'success': True,
                    'value': prescription_id_extracted,
                    'confidence': 0.9
                }
        return {
            'success': False,
            'value': f"Unknown field type: {field_type}",
            'confidence': 0.0
        }
    
    except Exception as e:
        logger.error(f"Error extracting patient info: {str(e)}")
        return {
            'success': False,
            'value': f"An error occurred while processing your request: {str(e)}",
            'confidence': 0.0
        }
