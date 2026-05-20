from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import ssl

user = os.getenv('DB_USER', 'portfolio_user')
password = os.getenv('DB_PASSWORD', 'portfolio_pass')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_NAME', 'portfolio_data')

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

USE_SSL = os.getenv("USE_SSL","true").lower() == "true"

if USE_SSL:
    cert_path = '/app/global-bundle.pem'
    ssl_context = ssl.create_default_context()
    if os.path.exists(cert_path):
        ssl_context.load_verify_locations(cert_path)
else:
    ssl_context = None


engine = create_async_engine(
    DATABASE_URL,
    connect_args = {"ssl":ssl_context}  
)

AsyncSessionLocal = sessionmaker(engine, class_ = AsyncSession, expire_on_commit= False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session