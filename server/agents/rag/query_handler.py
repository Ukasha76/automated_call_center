# server/agents/rag/query_handler.py
from datetime import datetime
from typing import Dict
import logging
import traceback
from .functions.generate_response import generate_response
from .functions.get_relevant_collection import get_relevant_collection
from .functions.retrieve_documents import retrieve_documents
import time
logger = logging.getLogger(__name__)

async def query_handler(
    query_data: Dict,
    llm,
    memory,
    prompt_template,
    get_session_info_func
) -> Dict:
    """Optimized query handling pipeline"""
    try:
        # Logic for recording stats
        agent_metadata = query_data.get('context', {}).get('agent_metadata', {})
        is_new_session = query_data.get('context', {}).get('is_new_session')
        
        # if is_new_session:
        agent_starting_time = time.time()

        query = query_data.get("text", "").strip()
    
        if not query:
            return _empty_query_response()
        
        logger.info(f"Processing query: {query}")
        
        steps_logs = []

        # Document retrieval pipeline - time recording for get_relevant_collection
        get_collection_start = time.time()
        collection_name = await get_relevant_collection(query)
        get_collection_end = time.time()

        steps_logs.append({
            "step_name": "get_relevant_collection",
            "step_duration_ms": (get_collection_end - get_collection_start) * 1000  # Convert to milliseconds
        })

        # Time recording for retrieve_documents
        retrieve_start = time.time()
        docs = await retrieve_documents(query, collection_name)
        retrieve_end = time.time()

        steps_logs.append({
            "step_name": "retrieve_documents",
            "step_duration_ms": (retrieve_end - retrieve_start) * 1000
        })
        
        if not docs:
            logger.warning(f"No documents found for query: {query}")
            return _no_documents_response()
        
        # Format context with enhanced metadata
        context = _format_document_context(docs)
        logger.info(f"Using {len(docs)} documents as context")
        
        # Time recording for generate_response
        generate_start = time.time()
        response = await generate_response(
            query=query,
            context=context,
            llm=llm,
            memory=memory,
            prompt_template=prompt_template,
            get_session_info_func=get_session_info_func
        )
        generate_end = time.time()
        
        steps_logs.append({
            "step_name": "generate_response",
            "step_duration_ms": (generate_end - generate_start) * 1000
        })
        
        # Prepare the full metrics package
        metrics_package = {
            "steps_logs": steps_logs,
        }
        agent_ending_time= time.time()
        # if is_new_session:
            # Initialize agent metadata with required fields
        agent_metadata = {
                'agent_starting_time': agent_starting_time,
                'agent_id': query_data.get('context', {}).get('agent_id', 'unknown'),
                'agent_name': 'RAG',
                'query_id': query_data.get('context', {}).get('query_id'),
                'query_text': query,
                'agent_completion_time':(agent_ending_time-agent_starting_time)*1000
            }
            
        # if is_new_session:
        response["agent_metadata"] = agent_metadata
        
        response["metrics"] = metrics_package
        response["agent_name"]="RAG"

        return response
        
    except Exception as e:
        logger.error(f"Query handling failed: {str(e)}\n{traceback.format_exc()}")
        return _error_response(str(e))

# Helper functions
def _format_document_context(docs: list) -> str:
    """Enhanced document formatting with metadata"""
    return "\n\n".join(
        f"""Document {i+1}: {doc.get('title', 'Untitled')}
 Relevance: {doc.get('score', 0):.2f}/1.0
 Last Updated: {doc.get('metadata', {}).get('updated', 'unknown')}
 Content: {doc.get('content', '')[:250]}..."""
        for i, doc in enumerate(docs)
    )

def _empty_query_response() -> Dict:
    return {
        "response": "Please provide a question about hospital services or policies.",
        "context_updates": {},
        "suggested_next": "RAG",
        "status": "active"
    }

def _no_documents_response() -> Dict:
    return {
        "response": ("I couldn't find specific information about that. "
                    "You might try:\n- Rephrasing your question\n"
                    "- Asking about admission, billing, or visiting hours\n"
                    "- Contacting the hospital directly"),
        "context_updates": {},
        "suggested_next": "RAG",
        "status": "active"
    }

def _error_response(error_msg: str) -> Dict:
    return {
        "response": f"System error: {error_msg}",
        "context_updates": {},
        "suggested_next": "HUMAN",
        "status": "resolved"
    }