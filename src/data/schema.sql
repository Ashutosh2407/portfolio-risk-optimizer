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


SELECT create_hypertable('ohlc', 'timestamp', if_not_exists => TRUE);

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
select create_hypertable('optimization_results','timestamp');

-- Create indexes for common queries
CREATE INDEX idx_optimization_strategy ON optimization_results(strategy);
CREATE INDEX idx_optimization_timestamp ON optimization_results(timestamp DESC);
CREATE INDEX idx_optimization_weights ON optimization_results USING GIN (weights);

