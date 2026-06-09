# contextlib allows us to manage what happens when the app starts and stops
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.routes.query import router as query_router
from app.routes.analytics import router as analytics_router

# This lifespan function runs before the server fully starts accepting requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # We call our database initialization to make sure tables are created
    print("Starting up: Checking database tables...")
    await init_db()
    print("Startup complete.")
    
    # yield tells FastAPI to start the server now
    yield
    
    # Anything after yield runs when the server is shutting down
    print("Shutting down Semantic Cache App...")

# We create our FastAPI application and tell it to use our lifespan function
app = FastAPI(
    title="LLM Semantic Cache",
    description="A semantic caching layer for LLMs to save time and money.",
    version="1.0.0",
    lifespan=lifespan
)

# We include the endpoints from query.py
app.include_router(query_router, tags=["Query"])

# We include the endpoints from analytics.py
app.include_router(analytics_router, tags=["Analytics"])

# We can run the app locally if we run this file directly
if __name__ == "__main__":
    import uvicorn
    # uvicorn is the server that actually runs our FastAPI app
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
