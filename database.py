import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session
from fastapi import FastAPI, Depends, BackgroundTasks, APIRouter
from schema import Base

# Load environment variables
load_dotenv()

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

# Update the DATABASE_URI for PostgreSQL
DATABASE_URI = f"mysql+aiomysql://{user}:{password}@{host}/{database}"

# Create asynchronous engine and session
engine = create_async_engine(DATABASE_URI, echo=True, pool_size=30)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)