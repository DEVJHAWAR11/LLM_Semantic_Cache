import time
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

# We import all the pieces we built in previous steps
from app.services.rate_limiter import check_rate_limit
from app.services.embedder import get_embedding
from app.services.cache import get_cached_response, store_in_cache
from app.services.llm import call_llm
from app.db.database import AsyncSessionLocal
from app.db.models import QueryLog

# APIRouter helps us organize our routes (like /ask) in different files
router = APIRouter()

# This tells FastAPI what data to expect from the user in the POST request body
class QueryRequest(BaseModel):
    query: str

# This creates a database session for us to use during the request, and safely closes it after
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# The actual endpoint that users will hit when they want to ask a question
@router.post("/ask")
async def ask_question(request: Request, body: QueryRequest, db=Depends(get_db)):
    # We start a timer to see how long the whole process takes
    start_time = time.time()
    
    # 1. Rate Limiting: Check if this IP is spamming us
    client_ip = request.client.host
    await check_rate_limit(client_ip)
    
    # We extract the user's question from the request body
    user_query = body.query
    
    # 2. Embedder: Convert the text into a 1024-number vector
    embedding = await get_embedding(user_query)
    
    # 3. Cache Check: See if we have answered this (or a very similar) question recently
    cache_result = await get_cached_response(embedding)
    
    # If we found it in the cache!
    if cache_result:
        # Calculate how many milliseconds it took
        latency_ms = (time.time() - start_time) * 1000
        
        # Log this event to our PostgreSQL database
        log_entry = QueryLog(
            query=user_query,
            response=cache_result["response"],
            cache_hit=True,
            latency_ms=latency_ms,
            tokens_used=None, # It didn't cost us any LLM tokens
            estimated_cost_usd=None # It didn't cost us any money
        )
        db.add(log_entry)
        await db.commit()
        
        # Return the cached answer to the user
        return {
            "response": cache_result["response"],
            "cache_hit": True,
            "latency_ms": round(latency_ms, 2)
        }
        
    # 4. Cache Miss: We have to call the Groq LLM
    llm_response, tokens = await call_llm(user_query)
    
    # We store this brand new answer in Redis for the next person
    await store_in_cache(user_query, embedding, llm_response)
    
    # Calculate how many milliseconds it took (will be much slower than a cache hit)
    latency_ms = (time.time() - start_time) * 1000
    
    # Groq pricing estimation (e.g., Llama 3 70B might be ~$0.00059 per 1k tokens)
    # We'll use a rough estimate for our logs
    estimated_cost = (tokens / 1000) * 0.00059
    
    # Log this expensive LLM call to our database
    log_entry = QueryLog(
        query=user_query,
        response=llm_response,
        cache_hit=False,
        latency_ms=latency_ms,
        tokens_used=tokens,
        estimated_cost_usd=estimated_cost
    )
    db.add(log_entry)
    await db.commit()
    
    # Return the fresh LLM answer to the user
    return {
        "response": llm_response,
        "cache_hit": False,
        "latency_ms": round(latency_ms, 2)
    }
