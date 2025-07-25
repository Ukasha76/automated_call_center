from .prompts.templates import get_hospital_prompt_template
from .models.embeddings import get_cohere_embeddings
from .utils.similarity import cosine_similarity
from .models.memory import initialize_memory
from .utils.session import get_session_info
from .models.llm import get_chat_groq_llm
from .query_handler import query_handler
import logging
from typing import  Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HospitalRAGSystem:
    def __init__(self, session_context: Optional[Dict] = None):

        # Initialize components from separate modules
        self.embeddings = get_cohere_embeddings()
        self.llm = get_chat_groq_llm()
        self.session_context = session_context or {}
        self.memory = initialize_memory(self.llm, self.session_context)
        self.prompt = get_hospital_prompt_template()
        self._get_session_info = get_session_info
        self.cosine_similarity = cosine_similarity

    async def handle_query(self, query_data: Dict) -> Dict:
        """Optimized query handling using the standalone function"""
        return await query_handler(
            query_data=query_data,
            llm=self.llm,
            memory=self.memory,
            prompt_template=self.prompt,
            get_session_info_func=self._get_session_info
        )
    
# Router-compatible interface
async def handle_query(query_data: Dict) -> Dict:
    """
    Public interface for router compatibility
    Args:
        query_data: {
            "text": "the user query",
            "context": {"session_id": "abc123", ...},
            "history": [previous exchanges]
        }
    Returns:
        Dict: {
            "response": "the generated response",
            "context_updates": {"new_info": "value"},
            "suggested_next": "optional department suggestion"
        }
    """
    try:
        # Create new instance with session context
        rag_system = HospitalRAGSystem(query_data.get("context", {}))
        response = await rag_system.handle_query(query_data)
        
        # Ensure response is properly formatted
        if not isinstance(response.get("response"), str):
            response["response"] = str(response["response"])
            
        return response
    except Exception as e:
        logger.error(f"Medical knowledge system error: {str(e)}")
        return {
            "response": f"Medical knowledge system error: {str(e)}",
            "context_updates": {},
            "suggested_next": "HUMAN"
        }

# Factory method for router compatibility
async def get_agent() -> HospitalRAGSystem:
    """Get the agent instance for routing system"""
    if 'rag_agent_instance' not in globals():
        global rag_agent_instance
        rag_agent_instance = HospitalRAGSystem()
    return rag_agent_instance

# Add initialize method to HospitalRAGSystem for router compatibility
def initialize(self) -> None:
    """Initialization method for router compatibility"""
    # Already initialized in __init__
    return

HospitalRAGSystem.initialize = initialize

if __name__ == "__main__":
    print("=== Starting application ===")