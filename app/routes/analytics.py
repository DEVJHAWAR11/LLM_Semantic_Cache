from fastapi import APIRouter, Depends
# We need SQLAlchemy tools to query the database and calculate averages/sums
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.models import QueryLog
from app.services.cache import clear_cache

# We create a new router for analytics
router = APIRouter()

# Same database session generator as before
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# This endpoint calculates our system's performance and cost savings
@router.get("/analytics")
async def get_analytics(db=Depends(get_db)):
    # Query 1: Total number of requests we have ever processed
    total_result = await db.execute(select(func.count(QueryLog.id)))
    total_queries = total_result.scalar() or 0
    
    # If no one has used the app yet, return zeros
    if total_queries == 0:
        return {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_rate_percent": 0.0,
            "avg_latency_hit_ms": 0.0,
            "avg_latency_miss_ms": 0.0,
            "estimated_cost_saved_usd": 0.0
        }
        
    # Query 2: Number of cache hits
    hits_result = await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.cache_hit == True)
    )
    cache_hits = hits_result.scalar() or 0
    cache_misses = total_queries - cache_hits
    
    # Calculate the percentage of queries that hit the cache
    hit_rate = (cache_hits / total_queries) * 100
    
    # Query 3: Average speed of cache hits
    avg_hit_lat = await db.execute(
        select(func.avg(QueryLog.latency_ms)).where(QueryLog.cache_hit == True)
    )
    avg_latency_hit = avg_hit_lat.scalar() or 0.0
    
    # Query 4: Average speed of cache misses (calls to Groq)
    avg_miss_lat = await db.execute(
        select(func.avg(QueryLog.latency_ms)).where(QueryLog.cache_hit == False)
    )
    avg_latency_miss = avg_miss_lat.scalar() or 0.0
    
    # Query 5: Average cost of a single Groq call
    avg_cost = await db.execute(
        select(func.avg(QueryLog.estimated_cost_usd)).where(QueryLog.cache_hit == False)
    )
    avg_miss_cost = avg_cost.scalar() or 0.0
    
    # The true value of semantic cache: Cost saved!
    # If we had 100 hits, we saved the cost of 100 LLM calls.
    cost_saved = cache_hits * avg_miss_cost

    return {
        "total_queries": total_queries,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "hit_rate_percent": round(hit_rate, 2),
        "avg_latency_hit_ms": round(avg_latency_hit, 2),
        "avg_latency_miss_ms": round(avg_latency_miss, 2),
        "estimated_cost_saved_usd": round(cost_saved, 4)
    }

# This endpoint wipes our Redis cache clean
@router.delete("/cache")
async def wipe_cache():
    # We call the clear_cache function we built in cache.py
    await clear_cache()
    
    return {
        "message": "Cache cleared successfully"
    }
