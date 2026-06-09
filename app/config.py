# importing BaseSettings from pydantic_settings. This helps us read from our .env file automatically.
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # these variables must match exactly what is in our .env file
    
    # API key for calling Groq LLMs
    GROQ_API_KEY: str
    
    # API key for calling Jina Embeddings API
    JINA_API_KEY: str
    
    # Redis configuration. host is 'localhost' locally, but 'redis' in docker-compose.
    REDIS_HOST: str
    REDIS_PORT: int
    
    # Connection string for PostgreSQL database
    DATABASE_URL: str
    
    # How similar two queries must be to count as a cache hit (e.g. 0.85 means 85%)
    SIMILARITY_THRESHOLD: float
    
    # How long cache entries live in seconds (86400 seconds = 24 hours)
    CACHE_TTL_SECONDS: int
    
    class Config:
        # this tells pydantic to look for a file named .env
        env_file = ".env"

# we create one instance of Settings that all other files will import and use
settings = Settings()
