import requests
import os 

api_url = os.getenv("API_URL","http://localhost:8000")

def get_tickers():
    try:
        response = requests.get(f"{api_url}/tickers")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError("Could not connect to API.")
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("API request timed out.")
    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError(f"API returned an error.")

def get_latest_result():
    try:
        response = requests.get(f"{api_url}/results/latest")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}


def get_results_history(limit=20):
    try:
        response = requests.get(f"{api_url}/results/history", params={"limit":limit})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError("Connection Error.")
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError("HTTP Error.")

def run_optimizer(tickers:list,strategy:str = "max_sharpe"):
    params = [("tickers",t) for t in tickers]
    params.append(("strategy", strategy))
    try:
        response = requests.get(f"{api_url}/optimize",params=params)
        if response.status_code ==200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}

def get_risk(tickers:list, weights: list):
    params = [("tickers",t) for t in tickers] + [("weights",float(w)) for w in weights]
    try:
        response = requests.get(f"{api_url}/risk", params=params)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}

def get_backtest(tickers:list,strategy:str):
    params = [("tickers",t) for t in tickers] + [("strategy", strategy)]
    try:
        response = requests.get(f"{api_url}/backtest", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError("Connection Error.")
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError("HTTP Error.")