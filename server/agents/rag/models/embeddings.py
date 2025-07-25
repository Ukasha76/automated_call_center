from langchain_cohere import CohereEmbeddings
import os

def get_cohere_embeddings():
    return CohereEmbeddings(
        model="embed-english-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY")
    )