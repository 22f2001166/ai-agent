import requests
from config import API_KEY, API_URL


def get_embedding(text: str):
    payload = {"api_key": API_KEY, "prompt": text, "model_id": "amazon-embedding-v2"}
    headers = {"Content-Type": "application/json"}
    res = requests.post(API_URL, headers=headers, json=payload)
    return res.json()["response"]["embedding"]
