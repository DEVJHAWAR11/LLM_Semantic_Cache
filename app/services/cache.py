import json
# importing the redis library to talk to our Redis database
import redis.asyncio as redis
from app.config import settings
from app.services.embedder import cosine_similarity

# setting up the connection to Redis. decode_responses=True means we get normal strings back instead of bytes
# which makes our lives much easier!
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

# This function searches the cache for a similar question
async def get_cached_response(new_embedding: list[float]) -> dict | None:
    # First we get how many items are in our cache right now. If none, we return None.
    count_str = await r.get("cache:count")
    if not count_str:
        return None
        
    count = int(count_str)
    
    # We will loop through every cache entry and check its similarity
    best_score = 0.0
    best_response = None
    best_key = None
    
    for i in range(count):
        cache_key = f"cache:{i}"
        
        # We read the embedding field from the Redis Hash. It's stored as a JSON string.
        stored_embedding_str = await r.hget(cache_key, "embedding")
        if not stored_embedding_str:
            continue
            
        # Convert the JSON string back into a Python list of floats
        stored_embedding = json.loads(stored_embedding_str)
        
        # Calculate similarity between the new question's vector and the stored vector
        score = cosine_similarity(new_embedding, stored_embedding)
        
        # If this score is the highest we've seen, remember it
        if score > best_score:
            best_score = score
            best_key = cache_key
            
    # If the best score we found is above our threshold (0.85), it's a hit!
    if best_score >= settings.SIMILARITY_THRESHOLD:
        # We get the response from the Redis Hash
        response = await r.hget(best_key, "response")
        
        # We also increment the hit_count for this entry so we know it's popular
        await r.hincrby(best_key, "hit_count", 1)
        
        return {
            "response": response,
            "similarity_score": best_score
        }
        
    # If we didn't find anything similar enough, return None (a cache miss)
    return None

# This function saves a new question and its answer to Redis
async def store_in_cache(query: str, embedding: list[float], response: str):
    # First, we increment the global counter to get the ID for our new entry
    new_id = await r.incr("cache:count") - 1
    cache_key = f"cache:{new_id}"
    
    # We save all fields into the Redis Hash
    # The embedding list must be converted to a JSON string first
    await r.hset(cache_key, mapping={
        "query": query,
        "embedding": json.dumps(embedding),
        "response": response,
        "hit_count": 0
    })
    
    # Finally, we set an expiration time (TTL) so this entry automatically deletes itself after 24 hours
    await r.expire(cache_key, settings.CACHE_TTL_SECONDS)

# This function completely wipes our cache
async def clear_cache():
    # We ask Redis to delete everything and reset
    await r.flushdb()
    
# Test block for testing this file independently
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing cache storage...")
        # create a dummy embedding of 1024 ones
        dummy_embedding = [1.0] * 1024
        
        await clear_cache()
        await store_in_cache("what is python", dummy_embedding, "Python is a programming language.")
        
        # Now try to retrieve it using a similar dummy embedding
        dummy_search = [0.99] * 1024
        result = await get_cached_response(dummy_search)
        
        print("Search result:", result)
        
    asyncio.run(test())
