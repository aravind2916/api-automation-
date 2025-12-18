import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Exact URL and Payload from working debug_auth_v2.py
LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

LOGIN_PAYLOAD = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "password": "dfaa43cb4002f53d61e9a36b3353bd79820f42337a7adccdce69d04fc076",
    "remember_me": True
}

_token_cache = None


def get_token():
    global _token_cache

    if _token_cache:
        return _token_cache

    print(f"Logging in to {LOGIN_URL}...")
    resp = requests.post(
        LOGIN_URL,
        json=LOGIN_PAYLOAD,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"DEBUG_API: URL: {resp.request.url}")
        print(f"DEBUG_API: Body: {resp.request.body}")
        print(f"DEBUG_API: Headers: {resp.request.headers}")
        raise RuntimeError(f"Login failed: {resp.text}")

    # Return full token object (verified required format)
    _token_cache = resp.json()["token"]
    return _token_cache


def api_request(method, url, **kwargs):
    headers = kwargs.pop("headers", {})

    # Verified Header Format: Bearer <json_string>
    headers["Authorization"] = f"Bearer {json.dumps(get_token())}"
    headers["Content-Type"] = "application/json"

    return requests.request(
        method=method,
        url=url,
        headers=headers,
        verify=False,
        timeout=30,
        **kwargs
    )
