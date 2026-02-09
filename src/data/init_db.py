"""
Initialize database schema
Run this once to create all tables
"""

from db_client import DatabaseClient
import os

def main():
    """
    Driver program for db_client.py
    
    """
    print("=" * 50)
    print("DATABASE INITIALIZATION")
    print("=" * 50)

    #CHECK IF SCHEMA FILE EXISTS
    schema_file = os.path.join(os.path.dirname(__file__),"schema.sql")

    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return
    
    print("\n Connecting to database...")
    try:
        db = DatabaseClient()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    print("Connected successfully")
    
    print("\nCreating tables...")

    try:
        db.initialize_schema(schema_file)
        print("Schema Initializer...")
    except Exception as e:
        print(f"Could not initialize schema: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ DATABASE READY!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run: python src/data/collector.py")
    print("2. This will backfill historical data")

if __name__ == "__main__":
    main()



    