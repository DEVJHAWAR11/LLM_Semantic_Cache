# importing tools from SQLAlchemy to define our database table structure
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
# importing the declarative base which all our models will inherit from
from sqlalchemy.orm import declarative_base
# importing datetime to set the default time for created_at
from datetime import datetime, timezone

# Base is a template class that SQLAlchemy uses to keep track of all our tables
Base = declarative_base()

# This class represents a single row in our query_logs table
class QueryLog(Base):
    # The name of the table in the PostgreSQL database
    __tablename__ = "query_logs"

    # id is the primary key. It will automatically increment for each new row.
    id = Column(Integer, primary_key=True, index=True)
    
    # query stores the exact question the user asked
    query = Column(String, nullable=False)
    
    # response stores the answer we returned (either from cache or from Groq)
    response = Column(String, nullable=False)
    
    # cache_hit is True if we found the answer in Redis, False if we had to call the LLM
    cache_hit = Column(Boolean, nullable=False)
    
    # latency_ms tracks how fast the request was in milliseconds
    latency_ms = Column(Float, nullable=False)
    
    # tokens_used stores how many tokens Groq processed. It is empty (nullable=True) if cache_hit is True.
    tokens_used = Column(Integer, nullable=True)
    
    # estimated_cost_usd stores how much the Groq call cost. It is empty if cache_hit is True.
    estimated_cost_usd = Column(Float, nullable=True)
    
    # created_at stores the exact time the request happened. Using timezone=True fixes asyncpg datetime errors.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
