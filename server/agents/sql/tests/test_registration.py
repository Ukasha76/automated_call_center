import sys
import os
from pathlib import Path
import asyncio
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockRegistrationTool:
    def __init__(self):
        self.current_step = "get_name"
        self.collected_data = {}

    async def invoke(self, input_data: str | Dict, context: Dict = None) -> Dict:
        """Mock registration tool for testing"""
        try:
            # Handle both structured and direct input
            if isinstance(input_data, dict):
                query = input_data.get('input_data', '')
                ctx = input_data.get('context', {}) or context or {}
            else:
                query = input_data
                ctx = context or {}

            # Get current step from context or use default
            self.current_step = ctx.get('current_step', 'get_name')
            self.collected_data = ctx.get('collected_data', {})

            # Process based on current step
            if self.current_step == 'get_name':
                if not query:
                    return {
                        'response': "Let's start your registration. What is your name?",
                        'current_step': 'get_name',
                        'collected_data': self.collected_data,
                        'status': 'in_progress'
                    }
                self.collected_data['name'] = query
                return {
                    'response': "What is your gender? (Male/Female/Prefer not to say)",
                    'current_step': 'get_gender',
                    'collected_data': self.collected_data,
                    'status': 'in_progress'
                }
            elif self.current_step == 'get_gender':
                self.collected_data['gender'] = query
                return {
                    'response': "What is your phone number?",
                    'current_step': 'get_phone',
                    'collected_data': self.collected_data,
                    'status': 'in_progress'
                }
            elif self.current_step == 'get_phone':
                self.collected_data['phone_number'] = query
                return {
                    'response': "What is your age?",
                    'current_step': 'get_age',
                    'collected_data': self.collected_data,
                    'status': 'in_progress'
                }
            elif self.current_step == 'get_age':
                self.collected_data['age'] = query
                return {
                    'response': "What is your address?",
                    'current_step': 'get_address',
                    'collected_data': self.collected_data,
                    'status': 'in_progress'
                }
            elif self.current_step == 'get_address':
                self.collected_data['address'] = query
                return {
                    'response': f"Please confirm your details:\n" +
                              f"Name: {self.collected_data['name']}\n" +
                              f"Gender: {self.collected_data['gender']}\n" +
                              f"Phone: {self.collected_data['phone_number']}\n" +
                              f"Age: {self.collected_data['age']}\n" +
                              f"Address: {self.collected_data['address']}\n\n" +
                              f"Is this correct? (yes/no)",
                    'current_step': 'confirm',
                    'collected_data': self.collected_data,
                    'status': 'in_progress'
                }
            elif self.current_step == 'confirm':
                if query.lower() in ['yes', 'y']:
                    return {
                        'response': f"Great! You have been successfully registered.",
                        'current_step': 'complete',
                        'collected_data': self.collected_data,
                        'status': 'complete'
                    }
                else:
                    return {
                        'response': "Let's start over. What is your name?",
                        'current_step': 'get_name',
                        'collected_data': {},
                        'status': 'in_progress'
                    }

        except Exception as e:
            logger.error(f"Error in registration tool: {str(e)}")
            return {
                'response': f"An error occurred: {str(e)}",
                'current_step': self.current_step,
                'collected_data': self.collected_data,
                'status': 'error'
            }

async def test_single_input(input_text: str, context: dict = None):
    """Test the registration tool with a single input"""
    print(f"\nInput: {input_text}")
    
    # Initialize context if not provided
    if context is None:
        context = {}
    
    # Create mock tool instance
    tool = MockRegistrationTool()
    
    # Call the registration tool
    result = await tool.invoke({
        'input_data': input_text,
        'context': context
    })
    
    # Print results
    print(f"Response: {result['response']}")
    print(f"Current Step: {result.get('current_step', 'N/A')}")
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Collected Data: {json.dumps(result.get('collected_data', {}), indent=2)}")
    
    return result

async def main():
    """Run interactive test"""
    context = {}
    
    print("\nRegistration Tool Test")
    print("=====================")
    print("Type your inputs to test the registration flow.")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            # Get user input
            user_input = input("\nEnter your input (or 'exit' to quit): ").strip()
            
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
                
            # Test the input
            result = await test_single_input(user_input, context)
            
            # Update context for next iteration
            if 'current_step' in result:
                context['current_step'] = result['current_step']
            if 'collected_data' in result:
                context['collected_data'] = result['collected_data']
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 