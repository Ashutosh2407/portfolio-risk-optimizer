from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from typing import Dict, Iterable,Optional,Sequence,Text
import pandas as pd
import os,json
from dotenv import load_dotenv

load_dotenv()


class DatabaseClient():
    """
    Establishes connection with the database,
    initializes schema and
    adds the ohlc data to the database table.
    """
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

    def save_optimization_result(self,d: Dict):
        """Insert optimization data in optimization_results table"""
        
        query = text("""
            INSERT INTO optimization_results (strategy,
                     expected_annual_return, 
                     annual_volatility,
                     sharpe_ratio,
                     weights)  VALUES
            (:strategy, :expected_return, :volatility, :sharpe, :weights)
        """)

        with self.engine.connect() as conn:
            conn.execute(query, {
                 'strategy': d['strategy'],
                 'expected_return': float(d['expected_annual_return']),
                 'volatility': float(d['annual_volatility']),
                 'sharpe': float(d['sharpe_ratio']),
                 'weights': json.dumps(d['weights'])
            })
            conn.commit()
            print("added from db_client")

    def save_backtest_results(self, result):
        """Insert backtest result data in backtest_results table"""
        
        query = text("""INSERT INTO backtest_results 
                    (strategy,train_period,test_period,train_days,test_days,optimal_weights,
                     realized_return,realized_volatility,realized_sharpe,max_drawdown,total_return,
                     benchmark_return,benchmark_volatility,benchmark_sharpe,benchmark_max_drawdown,
                     benchmark_total_return)
                     VALUES
                     (:strategy,:train_period,:test_period,:train_days,:test_days,:optimal_weights,
                     :realized_return,:realized_volatility,:realized_sharpe,:max_drawdown,:total_return,
                     :benchmark_return,:benchmark_volatility,:benchmark_sharpe,:benchmark_max_drawdown,
                     :benchmark_total_return);
                     """)
        
        with self.engine.connect() as conn:
            conn.execute(query, {
                "strategy": result["strategy"],
                "train_period":result["train_period"],
                "test_period":result["test_period"],
                "train_days":result["train_days"],
                "test_days":result["test_days"],
                "optimal_weights":json.dumps(result["optimal_weights"]),
                "realized_return":float(result["realized_return"]),
                "realized_volatility":float(result["realized_volatility"]),
                "realized_sharpe":float(result["realized_sharpe"]),
                "max_drawdown":float(result["max_drawdown"]),
                "total_return":float(result["total_return"]),
                "benchmark_return":float(result["benchmark_return"]),
                "benchmark_volatility":float(result["benchmark_volatility"]),
                "benchmark_sharpe":float(result["benchmark_sharpe"]),
                "benchmark_max_drawdown":float(result["benchmark_max_drawdown"]),
                "benchmark_total_return":float(result["benchmark_total_return"])
            })

            conn.commit()
            print(f"Inserted Backtest results into DB.")