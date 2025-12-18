import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

# Payload with 'username' instead of 'email'
LOGIN_PAYLOAD = {
    "username": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "isSuperAdmin": False,
    "password": "dfaa43cb4002f53d61e9a36b10ba6e5c31f04a974636f48adccdce69d04fc076",
    "remember_me": True
}

print(f"Logging in to {LOGIN_URL} with USERNAME key...")
resp = requests.post(
    LOGIN_URL,
    json=LOGIN_PAYLOAD,
    headers={"Content-Type": "application/json"},
    verify=False,
    timeout=30,
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
