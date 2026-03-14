import requests

base_url = "http://localhost:8000"

def get_tickers():
    try:
        response = requests.get(f"{base_url}/tickers")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
         {"error": "Could not connect to API. "}

def get_latest_result():
    try:
        response = requests.get(f"{base_url}/results/latest")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}


def get_results_history(limit=20):
    try:
        response = requests.get(f"{base_url}/results/history", params={"limit":limit})
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}

def run_optimizer(tickers:list,strategy:str = "max_sharpe"):
    params = [("tickers",t) for t in tickers]
    params.append(("strategy", strategy))
    try:
        response = requests.get(f"{base_url}/optimize",params=params)
        if response.status_code ==200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}

def get_risk(tickers:list, weights: list):
    params = [("tickers",t) for t in tickers] + [(weights,w) for w in weights]
    try:
        response = requests.get(f"{base_url}/risk", params=params)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError as e:
        return {"error": e}


