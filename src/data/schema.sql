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