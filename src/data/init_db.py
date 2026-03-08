"""
Initialize database schema
Run this once to create all tables
"""

from db_client import DatabaseClient
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """
    Driver program for db_client.py
    
    """
    print("=" * 50)
    logger.info("DATABASE INITIALIZATION")
    print("=" * 50)

    #CHECK IF SCHEMA FILE EXISTS
    schema_file = os.path.join(os.path.dirname(__file__),"schema.sql")

    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return
    
    logger.info("\n Connecting to database...")
    try:
        db = DatabaseClient()
    except Exception as e:
        logger.info(f"Error connecting to database: {e}")
        return

    logger.info("Connected successfully")
    
    logger.info("\nCreating tables...")

    try:
        db.initialize_schema(schema_file)
        logger.info("Schema Initializer...")
    except Exception as e:
        logger.info(f"Could not initialize schema: {e}")
        return
    
    print("\n" + "=" * 50)
    logger.info("✅ DATABASE READY!")
    print("=" * 50)
    

if __name__ == "__main__":
    main()



    