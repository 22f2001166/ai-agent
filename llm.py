import requests
from config import API_URL, API_KEY


def query_llm(prompt, model_id="claude-3.5-sonnet", max_tokens=512, temperature=0.3):
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": API_KEY,
        "prompt": prompt,
        "model_id": model_id,
        "model_params": {"max_tokens": max_tokens, "temperature": temperature},
    }
    response = requests.post(API_URL, json=data, headers=headers)
    return response.json()["response"]["content"][0]["text"]
