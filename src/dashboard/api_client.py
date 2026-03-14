import requests

base_url = "http://localhost:8000"

def get_latest_result():
    response = requests.get(f"{base_url}/results/latest")
    if response.status_code == 200:
        return response.json()
    return {"error": response.json().get("detail", "unknown error.")}


def get_results_history(limit=20):
    response = requests.get(f"{base_url}/results/history", params={"limit":limit})
    if response.status_code == 200:
        return response.json()
    return {"error": response.json().get("detail", "unknown error.")}

def run_optimizer(tickers:list,strategy:str = "max_sharpe"):
    params = [("tickers",t) for t in tickers]
    params.append(("strategy", strategy))
    response = requests.get(f"{base_url}/optimize",params=params)
    if response.status_code ==200:
        return response.json()
    return {"error": response.json().get("detail", "unknown error.")}

def get_risk(tickers:list, weights: list):
    params = [("tickers",t) for t in tickers] + [(weights,w) for w in weights]
    response = requests.get(f"{base_url}/risk", params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": response.json().get("detail", "unknown error.")}


