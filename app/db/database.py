# importing async database tools from SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# importing our Base and models to ensure they are registered
from app.db.models import Base
# importing our config settings to get the DATABASE_URL
from app.config import settings

# create_async_engine sets up the connection pool to our PostgreSQL database
# echo=False means it won't print every single SQL query to the terminal
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# async_sessionmaker creates new database sessions for us to use when we want to read/write data
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False # This keeps our objects available even after we save them to the database
)

# This function creates all the tables we defined in models.py (if they don't already exist)
async def init_db():
    # We open a connection to the database
    async with engine.begin() as conn:
        # We tell SQLAlchemy to create the tables based on our Base template
        await conn.run_sync(Base.metadata.create_all)

# Below is a simple block to test our code if we run this file directly
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Initializing database tables...")
        # Running the function to create the tables
        await init_db()
        print("Tables created successfully!")
        
    # asyncio.run is required because test() is an async function
    asyncio.run(test())
