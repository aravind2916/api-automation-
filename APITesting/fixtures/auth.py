import json
import requests

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

LOGIN_PAYLOAD = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "isSuperAdmin": False,
    "password": "dfaa43cb4002f53d61e9a36b10ba6e5c31f04a974636f48adccdce69d04fc076",
    "remember_me": True
}

_TOKEN_CACHE = None


def login_and_get_token_object():
    global _TOKEN_CACHE

    if _TOKEN_CACHE:
        return _TOKEN_CACHE

    resp = requests.post(
        LOGIN_URL,
        json=LOGIN_PAYLOAD,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30,
    )

    print("LOGIN status:", resp.status_code)

    assert resp.status_code == 200, f"Login failed: {resp.text}"

    _TOKEN_CACHE = resp.json()["token"]
    return _TOKEN_CACHE


def api_request(method, url, **kwargs):
    token_obj = login_and_get_token_object()

    headers = kwargs.pop("headers", {})

    # ✅ EXACT Postman behavior
    headers["Authorization"] = f"aBearer{json.dumps(token_obj)}"
    headers["Content-Type"] = "application/json"

    return requests.request(
        method=method,
        url=url,
        headers=headers,
        verify=False,
        timeout=30,
        **kwargs
    )
