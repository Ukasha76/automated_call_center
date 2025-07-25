import asyncio
import logging
from server.agents.sql.tools.functions.doctor_details.get_doctor_name import extract_doctor_details

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_doctor_search():
    test_cases = [
        "Dr. Angela Webb",
        "Angela Webb",
        "Dr. Webb",
        "Webb",
        "Angela",
        "Dr. Angela",
        "Tell me about Dr. Angela Webb",
        "What does Dr. Angela Webb specialize in?",
        "Details of Dr. Angela Webb"
    ]
    
    print("\nTesting Doctor Search Functionality")
    print("===================================")
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        try:
            result = await extract_doctor_details(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_doctor_search()) 