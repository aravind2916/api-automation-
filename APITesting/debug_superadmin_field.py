import requests
import hashlib
import urllib3
import json

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
pwd_raw = "Aravind@123"
pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

print(f"Testing with hash: {pwd_hash}")

# Test WITH isSuperAdmin
payload1 = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "password": pwd_hash,
    "remember_me": True,
    "isSuperAdmin": False
}

print("\nTest 1: WITH isSuperAdmin=False")
print(f"Payload: {json.dumps(payload1, indent=2)}")
resp1 = requests.post(url, json=payload1, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:200]}\n")

# Test WITHOUT isSuperAdmin
payload2 = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "password": pwd_hash,
    "remember_me": True
}

print("Test 2: WITHOUT isSuperAdmin")
print(f"Payload: {json.dumps(payload2, indent=2)}")
resp2 = requests.post(url, json=payload2, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text[:200]}")
