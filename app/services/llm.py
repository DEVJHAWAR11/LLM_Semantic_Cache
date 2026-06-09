# importing the Groq client which lets us talk to the Groq API
from groq import AsyncGroq
from app.config import settings
from fastapi import HTTPException

# We create our Groq client and pass it our API key from the config
client = AsyncGroq(api_key=settings.GROQ_API_KEY)

# This function sends the user's question to Groq and gets the answer
async def call_llm(query: str) -> tuple[str, int]:
    try:
        # We tell Groq what model to use and pass in the user's query
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            # This is the specific model we were told to use
            model="llama3-70b-8192",
        )
        
        # We extract the text answer from the API response
        response_text = chat_completion.choices[0].message.content
        
        # We also extract how many tokens were used so we can log it
        tokens_used = chat_completion.usage.total_tokens
        
        return response_text, tokens_used
        
    except Exception as e:
        # If anything goes wrong (like a bad API key or Groq is down), we catch the error
        # and throw a 500 Internal Server Error so our app doesn't completely crash
        raise HTTPException(status_code=500, detail=f"LLM API Error: {str(e)}")

# Test block
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing LLM call...")
        try:
            response, tokens = await call_llm("What is 2+2? Answer in one word.")
            print(f"Response: {response}")
            print(f"Tokens used: {tokens}")
        except Exception as e:
            print(f"Test failed: {e}")
            
    asyncio.run(test())
