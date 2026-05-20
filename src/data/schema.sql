CREATE TABLE IF NOT EXISTS ohlc (
    id serial,
    timestamp TIMESTAMPTZ NOT NULL,
    ticker varchar(10) not null,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4), 
    volume BIGINT,
    volume_weighted_avg_price DECIMAL(12,4),
    transactions BIGINT
);


--SELECT create_hypertable('ohlc', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_symbol_time ON ohlc (ticker, timestamp DESC);

CREATE TABLE IF NOT EXISTS optimization_results (
    id serial,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy TEXT NOT NULL,
    expected_annual_return DOUBLE PRECISION,
    annual_volatility DOUBLE PRECISION,
    sharpe_ratio DOUBLE PRECISION,
    weights JSONB NOT NULL
);

-- Convert to hypertable for time-series optimization
--select create_hypertable('optimization_results','timestamp',if_not_exists => TRUE);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_optimization_strategy ON optimization_results(strategy);
CREATE INDEX IF NOT EXISTS idx_optimization_timestamp ON optimization_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_optimization_weights ON optimization_results USING GIN (weights);

CREATE TABLE IF NOT EXISTS backtest_results(
    id serial,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy TEXT NOT NULL,
    train_period TEXT NOT NULL,
    test_period TEXT NOT NULL,
    train_days INTEGER,
    test_days INTEGER,
    optimal_weights JSONB NOT NULL,
    realized_return DOUBLE PRECISION,
    realized_volatility DOUBLE PRECISION, 
    realized_sharpe DOUBLE PRECISION, 
    max_drawdown DOUBLE PRECISION, 
    total_return DOUBLE PRECISION, 
    benchmark_return DOUBLE PRECISION,
    benchmark_volatility DOUBLE PRECISION,
    benchmark_sharpe DOUBLE PRECISION,
    benchmark_max_drawdown DOUBLE PRECISION,
    benchmark_total_return DOUBLE PRECISION
);

-- Convert to hypertable for time-series optimization
--select create_hypertable('backtest_results', 'timestamp',if_not_exists => TRUE);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_backtest_result_strategy ON backtest_results(strategy);
CREATE INDEX IF NOT EXISTS idx_backtest_result_timestamp ON backtest_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_result_weights ON backtest_results USING GIN (optimal_weights);