import httpx
import math
# importing settings from our config file to get the Jina API key
from app.config import settings

# This function sends our text to Jina AI and gets back a list of 1024 numbers (the embedding)
async def get_embedding(text: str) -> list[float]:
    # URL provided by Jina AI for their embeddings API
    url = "https://api.jina.ai/v1/embeddings"
    
    # Setting up the headers with our secret API key to prove we have an account
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.JINA_API_KEY}"
    }
    
    # We send the text and tell them which model we want to use
    data = {
        "model": "jina-embeddings-v3",
        "input": [text]
    }
    
    # We use httpx.AsyncClient to make the network request without blocking our app
    async with httpx.AsyncClient() as client:
        # We send a POST request with the data
        response = await client.post(url, headers=headers, json=data)
        
        # If the request fails (e.g. bad API key), this will raise an error
        response.raise_for_status()
        
        # We parse the JSON response from Jina AI
        result = response.json()
        
        # The embedding vector is hidden inside the 'data' list in the response
        embedding = result["data"][0]["embedding"]
        return embedding

# This function compares two embeddings (lists of numbers) and returns a score from -1 to 1
# A score close to 1 means the two texts have very similar meanings.
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    # First we calculate the dot product (multiplying matching positions and adding them up)
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Then we calculate the magnitude (length) of the first vector
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    
    # And the magnitude of the second vector
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    # If either vector is completely zero, similarity is 0 to avoid dividing by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
        
    # Finally, we divide the dot product by the multiplied magnitudes
    return dot_product / (magnitude1 * magnitude2)

# Below is a simple block to test our code if we run this file directly
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing get_embedding...")
        vector = await get_embedding("hello world")
        print(f"Embedding length: {len(vector)}") # Should print 1024
        
        # Testing similarity with same vector
        sim = cosine_similarity(vector, vector)
        print(f"Similarity with itself: {sim}") # Should print ~1.0
        
    asyncio.run(test())
