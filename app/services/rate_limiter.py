from fastapi import HTTPException
import redis.asyncio as redis
from app.config import settings

# Setting up our Redis connection just like in cache.py
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

# This function checks if an IP address is allowed to make another request
async def check_rate_limit(ip_address: str):
    # We create a unique key in Redis for this IP address
    key = f"rate:{ip_address}"
    
    # We read the current number of requests this IP has made
    current_count = await r.get(key)
    
    if current_count is None:
        # If the key doesn't exist, this is their first request.
        # We set their count to 1 and make the key expire in 60 seconds.
        await r.setex(key, 60, 1)
    else:
        # If the key exists, we check if they have hit the limit of 10 requests per minute
        if int(current_count) >= 10:
            # If they hit the limit, we throw a 429 Too Many Requests error
            # This automatically stops the FastAPI request and returns an error to the user
            raise HTTPException(status_code=429, detail="Too Many Requests")
        
        # If they haven't hit the limit, we just increment their count by 1
        await r.incr(key)

# Test block
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing rate limiter...")
        test_ip = "192.168.1.1"
        
        # We clear the key first to ensure a fresh test
        await r.delete(f"rate:{test_ip}")
        
        # We simulate 10 successful requests
        for i in range(10):
            await check_rate_limit(test_ip)
            print(f"Request {i+1} allowed")
            
        # The 11th request should fail
        try:
            await check_rate_limit(test_ip)
            print("Request 11 allowed (this is a bug!)")
        except HTTPException as e:
            print(f"Request 11 blocked as expected: {e.detail}")
            
    asyncio.run(test())
