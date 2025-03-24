import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create async engine for SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# For raw queries
database = Database(DATABASE_URL)

# Base model
Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session
