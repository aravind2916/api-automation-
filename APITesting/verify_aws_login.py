import requests
import json

# URL from conftest.py
LOGIN_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/auth/login"

# Payload from conftest.py
LOGIN_PAYLOAD = {
    "username": "aravind.m@gndsolutions.in",
    "password": "dfaa43cb4002f53d61e9a36b10ba6e5c31f04a974636f48adccdce69d04fc076"
}

urls_to_test = [
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/auth/login",
    "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/auth/login/"
]

for url in urls_to_test:
    print(f"Testing Login URL: {url}")
    try:
        resp = requests.post(url, json=LOGIN_PAYLOAD, timeout=30, verify=False)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")
