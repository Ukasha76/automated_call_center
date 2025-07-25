# from langchain_groq import ChatGroq
# import os
from langchain_ollama import ChatOllama



def get_chat_groq_llm():
    # return ChatGroq(
    #     model_name="gemma2-9b-it",
    #     temperature=0.2,
    #     api_key=os.getenv("GROQ_API_KEY")
    # )
    return ChatOllama(
        model = "llama3",
        temprature= 0.8,
        num_predict=256
    )