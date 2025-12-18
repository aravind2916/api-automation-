import requests

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

# Try the plaintext password found in tests/test_auth.py
ALTERNATIVE_PAYLOAD = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "isSuperAdmin": False,
    "password": "OldPass@123",
    "remember_me": True
}

print(f"Logging in to {LOGIN_URL} with OldPass@123...")
resp = requests.post(
    LOGIN_URL,
    json=ALTERNATIVE_PAYLOAD,
    headers={"Content-Type": "application/json"},
    verify=False,
    timeout=30,
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
