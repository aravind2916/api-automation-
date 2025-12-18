import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

_EMAIL = "aravind.m@gndsolutions.in"
_PASSWORD_HASH = "3a640839e1ccd43a2b13d53da9c99774d1913aa498ab97201ddc90c9a3e31b0c"

_access_token = None
_expiry = 0


def get_access_token(force=False):
    global _access_token, _expiry

    if not force and _access_token and time.time() < _expiry:
        return _access_token

    payload = {
        "email": _EMAIL,
        "authMethod": "PASSWORD",
        "password": _PASSWORD_HASH,
        "remember_me": True,
        "isSuperAdmin": False
    }

    resp = requests.post(LOGIN_URL, json=payload, verify=False, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    _access_token = data["access"]
    _expiry = time.time() + 55 * 60   # 55 minutes

    return _access_token
def get_token():
    import requests

    LOGIN_URL = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/auth/login"
    LOGIN_PAYLOAD = {
        "username": "aravind.m@gndsolutions.in",
        "password": "dfaa43cb4002f53d61e9a36b10ba6e5c31f04a974636f48adccdce69d04fc076"
    }

    response = requests.post(LOGIN_URL, json=LOGIN_PAYLOAD)
    response.raise_for_status()
    return response.json().get("access")

