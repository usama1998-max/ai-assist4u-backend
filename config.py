import asyncio
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create async engine for SQLAlchemy
engine = create_async_engine(DATABASE_URL ,pool_size=5, max_overflow=10, echo=True)

# Create session factory
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# For raw queries
database = Database(DATABASE_URL)

# Base model
Base = declarative_base()


async def get_db():
    loop = asyncio.get_running_loop()
    async with SessionLocal() as session:
        try:
            yield session  # ✅ Provide a fresh session for every request
        finally:
            await session.close()
