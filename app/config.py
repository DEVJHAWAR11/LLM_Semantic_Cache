# importing BaseSettings from pydantic_settings. This helps us read from our .env file automatically.
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # these variables must match exactly what is in our .env file
    
    # API key for calling Groq LLMs
    GROQ_API_KEY: str
    
    # API key for calling Jina Embeddings API
    JINA_API_KEY: str
    
    # We replaced REDIS_HOST and REDIS_PORT with a single REDIS_URL string for Upstash deployment
    REDIS_URL: str
    
    # Connection string for PostgreSQL database
    DATABASE_URL: str
    
    # How similar two queries must be to count as a cache hit (e.g. 0.85 means 85%).
    # We set default values so you don't have to manually enter them in Render!
    SIMILARITY_THRESHOLD: float = 0.85
    
    # How long cache entries live in seconds (86400 seconds = 24 hours)
    CACHE_TTL_SECONDS: int = 86400
    
    class Config:
        # this tells pydantic to look for a file named .env
        env_file = ".env"

# we create one instance of Settings that all other files will import and use
settings = Settings()
