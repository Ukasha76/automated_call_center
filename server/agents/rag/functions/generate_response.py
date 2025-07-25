from datetime import datetime
from typing import Dict, Optional
import logging
import traceback
from langchain.schema import HumanMessage

logger = logging.getLogger(__name__)

async def generate_response(
    query: str,
    context: str,
    llm,
    memory,
    prompt_template,
    get_session_info_func
) -> Dict:
    """Generate response that properly references retrieved documents"""
    try:
        # Get chat history
        chat_history = memory.chat_memory.messages if memory else []
        recent_history = "\n".join(
            f"{msg.type}: {msg.content}" 
            for msg in chat_history[-5:]
        ) if chat_history else ""

        # Format the prompt
        formatted_prompt = prompt_template.format(
            session_info=get_session_info_func(),
            current_date=datetime.now().strftime("%Y-%m-%d"),
            documents=context,
            chat_history=recent_history,
            query=query
        )
        
        logger.info(f"Generated prompt:\n{formatted_prompt}")

        # Get LLM response
        response = await llm.agenerate([[HumanMessage(content=formatted_prompt)]])
        response_content = response.generations[0][0].text if response.generations else ""
        logger.info(f"Raw response from LLM: {response_content}")

        # Clean and format response
        cleaned_response = _clean_response(response_content)
        
        # Update memory
        if memory:
            memory.save_context(
                {"query": query},
                {"response": cleaned_response}
            )

        return _format_final_response(query, cleaned_response)
        
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}\n{traceback.format_exc()}")
        return _generate_error_response()

def _clean_response(raw_response: str) -> str:
    """Clean and format the response text"""
    cleaned = raw_response.strip()
    if not cleaned:
        return "I'm sorry, but I couldn't find specific information about that in our documents. Is there anything else I can help you with?"
    
    if not cleaned.startswith(("I can help", "According to")):
        cleaned = f"I can help with that!\n\n{cleaned}"
    
    if not cleaned.endswith("Is there anything else I can help you with?"):
        cleaned = f"{cleaned}\n\nIs there anything else I can help you with?"
    
    logger.info(f"Final response to user: {cleaned}")
    return cleaned

def _format_final_response(query: str, response: str) -> Dict:
    """Package the final response structure"""
    timestamp = datetime.now().isoformat()
    return {
        "response": response,
        "context_updates": {
            "last_interaction": timestamp,
            "chat_history": [{
                "query": query,
                "response": response,
                "timestamp": timestamp
            }]
        },
        "chat_history": {
            'query': query,
            'response': response,
            'timestamp': timestamp
        },
        "suggested_next": None,
        "status": "resolved",
        
        
    }

def _generate_error_response() -> Dict:
    """Generate error response structure"""
    error_msg = "I encountered an error processing your request. Please try again."
    logger.info(f"Returning error message: {error_msg}")
    return {
        "response": error_msg,
        "context_updates": {},
        "suggested_next": "HUMAN"
    }