from langchain.memory import ConversationSummaryBufferMemory
from datetime import datetime

def initialize_memory(llm, session_context=None):
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        memory_key="chat_history",
        max_token_limit=2000,
        return_messages=True,
        input_key="query",
        output_key="response"
    )
    
    if session_context and "chat_history" in session_context:
        for exchange in session_context["chat_history"]:
            memory.save_context(
                {"query": exchange["query"]},
                {"text": exchange["response"]}
            )
    
    return memory