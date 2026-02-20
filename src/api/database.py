from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

user = os.getenv('DB_USER', 'portfolio_user')
password = os.getenv('DB_PASSWORD', 'portfolio_pass')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_NAME', 'portfolio_data')

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(engine, class_ = AsyncSession, expire_on_commit= False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session