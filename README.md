# LLM Semantic Cache

This project is a high-performance semantic caching layer for Large Language Models (LLMs). It intercepts user questions, converts them into mathematical vectors using Jina AI embeddings, and checks a Redis cache for semantically similar previous questions. If a match is found (>= 85% similarity), the cached answer is returned instantly, saving API costs and reducing latency from seconds to milliseconds.

## Architecture

```text
       User Request (POST /ask)
              │
              ▼
      [ Rate Limiter (Redis) ] ──(Block if >10 req/min)
              │
              ▼
   [ Jina Embeddings API ] ──(Converts text to 1024-d vector)
              │
              ▼
      [ Redis Cache Check ] ──(Cosine Similarity >= 0.85?)
              │
      ┌───────┴────────┐
   Hit (Yes)       Miss (No)
      │                │
      ▼                ▼
[ Return Fast ]   [ Groq LLM API ]
      │                │
      │                ▼
      │       [ Store in Redis ]
      │                │
      └───────┬────────┘
              ▼
   [ Log to PostgreSQL DB ]
```

## How To Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DEVJHAWAR11/LLM_Semantic_Cache.git
   cd LLM_Semantic_Cache
   ```

2. **Set up Environment Variables:**
   Copy the example environment file and fill in your API keys.
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your `GROQ_API_KEY` and `JINA_API_KEY`. (Keep `REDIS_HOST=redis` and `REDIS_PORT=6379` for Docker).

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```
   This will start three containers:
   - `redis`: In-memory data store for the cache and rate limiter.
   - `postgres`: Analytics database to store query logs.
   - `fastapi_app`: The main application running on port `8000`.

4. **Test the API:**
   Once running, you can access the interactive API docs at:
   [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

### 1. Ask a Question
`POST /ask`
Takes a user query, checks the cache, and either returns the cached response or calls the LLM.
**Request Body:**
```json
{
  "query": "What is machine learning?"
}
```
**Response:**
```json
{
  "response": "Machine learning is a subset of AI...",
  "cache_hit": false,
  "latency_ms": 1540.23
}
```

### 2. View Analytics
`GET /analytics`
Returns cache performance statistics and calculated cost savings.
**Response:**
```json
{
  "total_queries": 150,
  "cache_hits": 89,
  "cache_misses": 61,
  "hit_rate_percent": 59.3,
  "avg_latency_hit_ms": 23.4,
  "avg_latency_miss_ms": 1840.1,
  "estimated_cost_saved_usd": 0.43
}
```

### 3. Clear Cache
`DELETE /cache`
Wipes the Redis cache clean.
**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

## Tech Stack
- **FastAPI:** Chosen for its high performance, native async support, and auto-generated Swagger UI docs.
- **Redis:** Used as an in-memory vector store (via Hashes) and for rate limiting due to its blazing fast read/write speeds.
- **PostgreSQL:** Used for persistent analytics logging to track cache hit rates and cost savings.
- **Jina Embeddings v3:** Converts text into rich 1024-dimensional semantic vectors.
- **Groq API (Llama 3):** Powers the actual LLM generation. Groq was chosen for its incredibly fast inference speeds.
- **Docker & Docker Compose:** Containerizes the application and its dependencies for reliable, cross-platform deployment.
