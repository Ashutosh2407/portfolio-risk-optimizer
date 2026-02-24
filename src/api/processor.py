from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.data.db_client import DatabaseClient
from src.data.processor import MarketDataProcessor

def get_processor(db: DatabaseClient = Depends(DatabaseClient)) -> MarketDataProcessor:
    return MarketDataProcessor(db=db)