"""
Run backtest for portfolio optimization strategies.
"""

import sys
import numpy as np
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.processor import MarketDataProcessor
from src.models.backtest import Backtester
from src.data.db_client import DatabaseClient
from sqlalchemy import text
import json

def save_backtest_result(result):
    """Save backtest results to database"""
    db = DatabaseClient()

    query = text("""
        INSERT INTO  backtest_result 
                (timestamp,strategy,realized_return,realized_volatility,
                 realized_sharpe,max_drawdown, total_return, benchmark_return,
                 benchmark_volatility,benchmark_sharpe,benchmark_max_drawdown,benchmark_total_return,optimal_weights) 
                 VALUES 
                 (NOW(),:strategy,:realized_return,:realized_volatility,:realized_sharpe,
                 :max_drawdown,:total_return,:benchmark_return,:benchmark_volatility,:benchmark_sharpe,
                 :benchmark_max_drawdown,:benchmark_total_return,:optimal_weights);
                 RETURNING id;
                 """)
    
    with db.engine.connect() as conn:
        result_id = conn.execute(query, {
            "strategy": result["strategy"],
            "realized_return":result["realized_return"],
            "realized_volatility":result["realized_volatility"],
            "realized_sharpe":result["realized_sharpe"],
            "max_drawdown":result["max_drawdown"],
            "total_return":result["total_return"],
            "benchmark_return":result["benchmark_return"],
            "benchmark_volatility":result["benchmark_volatility"],
            "benchmark_sharpe":result["benchmark_sharpe"],
            "benchmark_max_drawdown":result["benchmark_max_drawdown"],
            "benchmark_total_return":result["benchmark_total_return"],
            "optimal_weights":result["optimal_weights"]
        })
        conn.commit()
        print(f"✅ Saved to database (ID: {result_id})")


def main():
    # Configuration
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'META', 'NVDA','JPM']

    print("=" * 70)
    print("PORTFOLIO OPTIMIZATION BACKTEST")
    print("=" * 70)
    print(f"Symbols: {symbols}")

    # Load data
    print("\n📊 Loading historical data...")
    processor = MarketDataProcessor(DatabaseClient())
    data = processor.load_ohlc_from_db(symbols)
    prices = processor.generate_price_matrix(data)
    returns = processor.generate_returns_matrix(prices)
    print(f" Loaded {len(returns)} days of data")

    #Run backtests for both strategies
    results = []

    for strategy in ['max_sharpe', 'min_volatility']:
        print(f"\n{'='*70}")
        print(f"{strategy.upper().replace('_', ' ')} STRATEGY")
        print(f"{'='*70}")
        
        backtester = Backtester(returns, strategy=strategy)
        result = backtester.run_backtest(train_period_days=252)
        results.append(result)

        # Display results
        print(f"\n📈 OUT-OF-SAMPLE PERFORMANCE ({result['test_days']} trading days)")
        print(f"   Period: {result['test_period']}")
        print(f"\n   Portfolio Strategy: {strategy}")
        print(f"      Return:     {result['realized_return']*100:>7.2f}%")
        print(f"      Volatility: {result['realized_volatility']*100:>7.2f}%")
        print(f"      Sharpe:     {result['realized_sharpe']:>7.2f}")
        print(f"      Max DD:     {result['max_drawdown']*100:>7.2f}%")
        print(f"      Total:      {result['total_return']*100:>7.2f}%")
        
        print(f"\n   Benchmark (Equal Weight):")
        print(f"      Return:     {result['benchmark_return']*100:>7.2f}%")
        print(f"      Volatility: {result['benchmark_volatility']*100:>7.2f}%")
        print(f"      Sharpe:     {result['benchmark_sharpe']:>7.2f}")
        print(f"      Max DD:     {result['benchmark_max_drawdown']*100:>7.2f}%")
        print(f"      Total:      {result['benchmark_total_return']*100:>7.2f}%")
        
        print(f"\n   📊 ALPHA:")
        print(f"      Return:     {(result['realized_return'] - result['benchmark_return'])*100:>7.2f}%")
        print(f"      Sharpe:     {result['realized_sharpe'] - result['benchmark_sharpe']:>7.2f}")
        print(f"      Total:      {(result['total_return'] - result['benchmark_total_return'])*100:>7.2f}%")
        
        # Save to database
        #save_backtest_result(result, symbols)
    
    # Summary comparison
    print(f"\n{'='*70}")
    print("STRATEGY COMPARISON")
    print(f"{'='*70}")
    print(f"{'Metric':<20} {'Max Sharpe':>15} {'Min Volatility':>15}")
    print(f"{'-'*70}")
    print(f"{'Return':<20} {results[0]['realized_return']*100:>14.2f}% {results[1]['realized_return']*100:>14.2f}%")
    print(f"{'Volatility':<20} {results[0]['realized_volatility']*100:>14.2f}% {results[1]['realized_volatility']*100:>14.2f}%")
    print(f"{'Sharpe Ratio':<20} {results[0]['realized_sharpe']:>15.2f} {results[1]['realized_sharpe']:>15.2f}")
    print(f"{'Max Drawdown':<20} {results[0]['max_drawdown']*100:>14.2f}% {results[1]['max_drawdown']*100:>14.2f}%")
    print(f"{'Total Return':<20} {results[0]['total_return']*100:>14.2f}% {results[1]['total_return']*100:>14.2f}%")
    print(f"{'='*70}")
    #print(results[0]['strategy'])
    # print(results[1])

if __name__ == "__main__":
    main()