from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from src.api.main import app
from src.api.database import get_db
from conftest import make_mock_db 



class TestHealthCheck:
    def test_health_returns_200(self,client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health_returns_ok_status(self,client):
        response = client.get("/")
        assert response.json()["status"] == "ok"

class TestResultsEndpoints:
    fake_row = {
        "id": 1, 
        "timestamp": "2026-02-25",
        "strategy": "max_sharpe",
        "expected_annual_return":0.011,
        "annual_volatility":0.052,
        "sharpe_ratio":1.2,
        "weights":{"AAPL":0.3,"MSFT":0.3}
        }
    
    fake_rows = [
            {"id": 1, "timestamp": "2026-02-25","strategy": "max_sharpe","expected_annual_return":0.011,
                    "annual_volatility":0.052,"sharpe_ratio":1.2,"weights":{"AAPL":0.3,"MSFT":0.3}},
            
            {"id": 2, "timestamp": "2026-02-25","strategy": "min_volatility","expected_annual_return":0.012,
                    "annual_volatility":0.072,"sharpe_ratio":1.5,"weights":{"AAPL":0.3,"MSFT":0.25}}
        ]

    def test_returns_404_when_empty(self,client):
        app.dependency_overrides[get_db] = lambda: make_mock_db(row=None)
        response = client.get("/results/latest")
        assert response.status_code == 404
        

    def test_returns_200_when_data_exists(self,client):
        app.dependency_overrides[get_db] = lambda: make_mock_db(row = self.fake_row)
        response = client.get("/results/latest")
        assert response.status_code == 200


    def test_latest_response_contains_expected_keys(self,client):
        app.dependency_overrides[get_db] = lambda:make_mock_db(row=self.fake_row)
        response = client.get("/results/latest")
        data = response.json()
        assert "timestamp" in data
        assert "strategy" in data
        assert "weights" in data
        assert "expected_annual_return" in data
        assert "annual_volatility" in data
        assert "sharpe_ratio" in data
        

    def test_history_returns_200(self,client):
        app.dependency_overrides[get_db] = lambda:make_mock_db(rows=[])
        response = client.get("/results/history")
        assert response.status_code ==200
        

    def test_history_returns_results_and_count(self,client):
        
        app.dependency_overrides[get_db] = lambda:make_mock_db(rows = self.fake_rows)
        response = client.get("/results/history")
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] == 2
        

    def test_history_limit_param(self,client):
        app.dependency_overrides[get_db] = lambda: make_mock_db(rows = [])
        response = client.get("/results/history?limit=5")
        assert response.status_code == 200
        

    def test_history_limit_too_high_returns_422(self,client):
        app.dependency_overrides[get_db] = lambda:make_mock_db(rows=[])
        response = client.get("/results/history?limit=999")
        assert response.status_code == 422

    def test_history_limit_zero_returns_422(self,client):
        response = client.get("/results/history?limit=0")
        assert response.status_code == 422
    
class TestOptimizeEndpoint:
    BASE_URL = "/optimize?tickers=AAPL&tickers=MSFT&tickers=JPM&tickers=GS&strategy=max_sharpe"

    #HAPPY PATH-------------------------------------------------------------------------------
    def test_optimize_returns_200(self,client):
        response = client.get(self.BASE_URL)
        assert response.status_code == 200

    def test_optimize_results_has_weights(self,client):
        response = client.get(self.BASE_URL)
        assert "weights" in response.json()

    def test_optimize_results_has_tickers(self,client):
        response = client.get(self.BASE_URL)
        assert "tickers" in response.json()

    def test_optimize_response_has_strategy(self, client):
        response = client.get(self.BASE_URL)
        assert "strategy" in response.json()

    def test_optimize_tickers_in_response(self,client):
        response = client.get(self.BASE_URL)
        assert set(response.json()["tickers"]) == {"AAPL", "MSFT", "JPM", "GS"}

    def test_optimize_strategy_in_response(self, client):
        response = client.get(self.BASE_URL)
        assert response.json()["strategy"] == "max_sharpe"

  
    # ── Strategy Routing ──────────────────────────────────────────────────────
    def test_max_sharpe_calls_correct_optimizer_method(self,client,mock_optimizer):
        client.get(self.BASE_URL)
        mock_optimizer.optimize_max_sharpe.assert_called_once()
    
    def test_min_volatility_calls_correct_optimizer_method(self,client,mock_optimizer):
        base = "/optimize?tickers=AAPL&tickers=MSFT&tickers=JPM&tickers=GS&strategy=min_vol"
        client.get(base)
        mock_optimizer.optimize_min_volatility.assert_called_once()

    def test_min_vol_returns_200(self, client):
        base = "/optimize?tickers=AAPL&tickers=MSFT&tickers=JPM&tickers=GS&strategy=min_vol"
        response = client.get(base)
        assert response.status_code == 200

    #Processor is called----------
    def test_processor_is_executed(self,client,mock_processor):
        client.get(self.BASE_URL)
        mock_processor.run.assert_called_once()

    #Check if tickers are uppercased before
    def test_if_tickers_are_uppercased_before_running_processor(self, client,mock_processor):
        client.get(self.BASE_URL)
        call_args = mock_processor.run.call_args[0][0]
        assert call_args == ["AAPL", "MSFT", "JPM", "GS"]

    #Validation--------------
    #Raw client — signals "this test needs no mocks, fails at validation layer"
    def test_missing_tickers_returns_422(self):
        response = TestClient(app=app).get("/optimize?strategy=max_sharpe")
        assert response.status_code == 422

    def test_invalid_strategy_returns_422(self):
        response = TestClient(app=app).get("/optimize?tickers=AAPL&tickers=MSFT&strategy=invalid_strategy")
        assert response.status_code == 422

class TestRiskEndpoint:
    BASE_URL ="/risk?tickers=AAPL&tickers=MSFT&tickers=JPM&weights=0.4&weights=0.35&weights=0.25"

    #status code 200
    def test_risk_endpoint_returns_200(self,client):
        response = client.get(self.BASE_URL)
        assert response.status_code == 200

    #expected keys
    def test_risk_endpoint_returns_expected_keys(self,client):
        response = client.get(self.BASE_URL)
        data = response.json()
        assert "tickers" in data
        assert "weights" in data
        assert "volatility" in data
        assert "max_drawdown" in data
        assert "var_95" in data
        assert "cvar" in data

    def test_risk_tickers_in_response(self, client):
        response = client.get(self.BASE_URL)
        assert set(response.json()["tickers"]) == {"AAPL", "MSFT", "JPM"}

    def test_risk_weights_in_response(self, client):
        response = client.get(self.BASE_URL)
        weights = response.json()["weights"]
        assert set(weights.keys()) == {"AAPL", "MSFT", "JPM"}
    
       # ── Processor is called ───────────────────────────────────────────────────

    def test_processor_run_is_called(self, client, mock_processor):
        client.get(self.BASE_URL)
        mock_processor.run.assert_called_once()

    def test_processor_receives_correct_tickers(self, client, mock_processor):
        client.get(self.BASE_URL)
        call_args = mock_processor.run.call_args[0][0]
        assert call_args == ["AAPL", "MSFT", "JPM"]
    
    # ── Validation ────────────────────────────────────────────────────────────

    def test_mismatched_tickers_and_weights_returns_422(self, client):
        response = client.get(
            "/risk?tickers=AAPL&tickers=MSFT&weights=0.5"  # 2 tickers, 1 weight
        )
        assert response.status_code == 422

    def test_weights_not_summing_to_one_returns_422(self, client):
        response = client.get(
            "/risk?tickers=AAPL&tickers=MSFT&weights=0.5&weights=0.8"  # sums to 1.3
        )
        assert response.status_code == 422

    def test_missing_tickers_returns_422(self):
        response = TestClient(app).get("/risk?weights=0.5&weights=0.5")
        assert response.status_code == 422

    def test_missing_weights_returns_422(self):
        response = TestClient(app).get("/risk?tickers=AAPL&tickers=MSFT")
        assert response.status_code == 422
