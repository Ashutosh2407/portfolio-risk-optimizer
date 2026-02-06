from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseClient():
    def __init__(self, connection_string = None):
        if not connection_string:
            user = os.getenv('DB_USER', 'portfolio_user')
            password = os.getenv('DB_PASSWORD', 'portfolio_pass')
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'portfolio_data')

            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def initialize_schema(self, schema_file):
        with open(schema_file,'r') as f:
            schema = f.read()
        
        statements = schema.split(';')
        with self.engine.connect() as conn:
            for statement in statements:
                if statement.strip():
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        if "already_exists" not in str(e):
                            print(f"{e}")

        print("Tables created successfully.")


    def insert_ohlc_batch(self, df):
        """Insert OHLC data in batch"""
        df.to_sql('ohlc',self.engine,if_exists = 'append', index = False, method = 'multi')
        print(f"Inserted {len(df)} records in database.")