import numpy as np

def cosine_similarity(vecA: list[float], vecB: list[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vecA, vecB)
    magnitudeA = np.linalg.norm(vecA)
    magnitudeB = np.linalg.norm(vecB)
    return dot_product / (magnitudeA * magnitudeB)