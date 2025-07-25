from typing import Dict
from ..models.embeddings import get_cohere_embeddings
from ..collection_config import COLLECTION_CONFIG  # Make sure this exists
from ..utils.similarity import cosine_similarity
# COLLECTION_CONFIG = {
#     "Department_Details": {
#         "chunk_size": 500,
#         "service": "department",
#         "fallback": "Department information is available at the information desk."
#     },
#     "General_Consulting": {
#         "chunk_size": 300,
#         "service": "outpatient",
#         "fallback": "General consulting hours are 9AM-5PM weekdays."
#     },
#     "Patient_Safety_Policy": {
#         "chunk_size": 500,
#         "service": "patient care",
#         "fallback": "Patient safety is our top priority. Please ask staff for specific policies."
#     },
#     "Outpatients_Policies": {
#         "chunk_size": 400,
#         "service": "outpatient",
#         "fallback": "Standard outpatient visiting hours are 9AM-5PM."
#     },
#     "Admission_Discharge": {
#         "chunk_size": 350,
#         "service": "hospital_admission",
#         "fallback": "Admission requires ID and insurance information. Please contact the admissions desk for assistance."
#     },
#     "Principles_Policies": {
#         "chunk_size": 300,
#         "service": "principles",
#         "fallback": "Our hospital follows international healthcare principles."
#     }
# }


async def get_relevant_collection(query: str) -> str:
    """Determine the most relevant collection using embeddings"""
    embeddings= get_cohere_embeddings()
    query_embedding = await embeddings.aembed_query(query)
    
    best_match = "Admission_Discharge"  # Default collection
    highest_score = -1

    for collection_name in COLLECTION_CONFIG.keys():
        collection_embedding = await embeddings.aembed_query(collection_name.replace("_", " "))
        similarity = cosine_similarity(query_embedding, collection_embedding)
        
        if similarity > highest_score:
            highest_score = similarity
            best_match = collection_name

    return best_match

# async def get_relevant_collection(self, query: str) -> str:
#         """Determine the most relevant collection using embeddings"""

#         query_embedding = await self.embeddings.aembed_query(query)

#         best_match = "Admission_Discharge"  # Default collection
#         highest_score = -1

#         for collection_name in COLLECTION_CONFIG.keys():
#             collection_embedding = await self.embeddings.aembed_query(collection_name.replace("_", " "))
#             similarity = self.cosine_similarity(query_embedding, collection_embedding)
            
#             if similarity > highest_score:
#                 highest_score = similarity
#                 best_match = collection_name

#         return best_match