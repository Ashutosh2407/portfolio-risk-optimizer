# 📈 Portfolio Risk Optimizer

A production-grade quantitative finance platform that optimizes stock portfolios using Modern Portfolio Theory, calculates risk metrics, and runs walk-forward backtests, served via a REST API and interactive dashboard.

**Live Demo:** [Coming Soon] | **API Docs:** [Coming Soon]

---

## 🔍 Overview

This project ingests daily OHLC market data, processes returns, and applies mean-variance optimization to construct efficient portfolios. It exposes results through a FastAPI backend and a Streamlit dashboard.

---

## ✨ Key Features

- **Portfolio Optimization** — Max Sharpe Ratio & Minimum Volatility strategies via PyPortfolioOpt.
- **Risk Metrics** — VaR (95%/99%), CVaR, Maximum Drawdown, Portfolio Volatility.
- **Walk-Forward Backtesting** — Train/test split with benchmark comparison (equal-weight).
- **REST API** — FastAPI with auto-generated Swagger docs.
- **Time-Series Database** — TimescaleDB (PostgreSQL) for OHLC and results storage.
- **Structured Logging** — Module-level logging with timestamps across all services.
- **Monitoring** — Prometheus metrics endpoint, Grafana dashboards.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API | FastAPI |
| Optimization | PyPortfolioOpt |
| Database | TimescaleDB (PostgreSQL) |
| ORM | SQLAlchemy (async) |
| Dashboard | Streamlit |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker + Docker Compose |
| Testing | Pytest |

---

## 🏗 Architecture
Market Data 
↓
collector.py → TimescaleDB
↓
processor.py (returns, covariance)
↓
optimizer.py → /optimize endpoint
risk.py → /risk endpoint
backtest.py → /backtest endpoint
↓
Streamlit Dashboard ←→ FastAPI


---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+


### Installation
```bash
git clone https://github.com/yourusername/portfolio-optimizer.git
cd portfolio-optimizer
cp .env.example .env        # fill in your values
docker-compose up -d
```

## Running Locally (without Docker)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

### 📡 API Endpoints
| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| GET    | /                | Health check               |
| GET    | /optimize        | Run portfolio optimization |
| GET    | /risk            | Calculate risk metrics     |
| GET    | /backtest        | Run walk-forward backtest  |
| GET    | /results/latest  | Latest optimization result |
| GET    | /results/history | All past optimizations     |
<!--| GET    | /metrics         | Prometheus metrics         | -->

Full docs available at /docs (Swagger UI) when the API is running.

## 📊 Example Usage
# Optimize a portfolio
```bash
curl "http://localhost:8000/optimize?tickers=AAPL&tickers=MSFT&tickers=GOOGL&strategy=max_sharpe"
```

# Get risk metrics
```bash
curl "http://localhost:8000/risk?tickers=AAPL&tickers=MSFT&weights=0.6&weights=0.4"
```

### 🧪 Running Tests
pytest tests/ -v

### 📁 Project Structure
portfolio-optimizer/
1) src/. \
    a) api/         # FastAPI app, endpoints.\
    b) models/       # optimizer, risk, backtest.\
    c) data/         # collector, processor, db_client. \
    d) monitoring/   # metrics. \
    e) utils/        # logger.
2) tests/
3) notebooks/
4) docker-compose.yml
5) Dockerfile
6) requirements.txt
7) .env.example
