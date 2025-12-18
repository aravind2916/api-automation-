
import sys
sys.path.append('.')
sys.path.append('tests')
import hashlib
import json
import requests
import urllib3
urllib3.disable_warnings()

# 1. Define expectations
EXPECTED_PASS = "Aravind@123"
EXPECTED_HASH = hashlib.sha256(EXPECTED_PASS.encode()).hexdigest()
print(f"Goal Password: {EXPECTED_PASS}")
print(f"Goal Hash:     {EXPECTED_HASH}")

# 2. Import conftest payload
try:
    from conftest import LOGIN_PAYLOAD
    print("\n--- conftest.py ---")
    print(f"Password in conftest: {LOGIN_PAYLOAD['password']}")
    if LOGIN_PAYLOAD['password'] == EXPECTED_HASH:
        print("MATCHES Goal Hash")
    else:
        print("DOES NOT MATCH Goal Hash")
    
    # Try request with conftest payload
    resp = requests.post("https://authentication.thinxview.com/api/auth/login/", json=LOGIN_PAYLOAD, verify=False)
    print(f"Conftest Request Status: {resp.status_code}")
except ImportError as e:
    print(f"Could not import conftest: {e}")

# 3. Construct manual payload
manual_payload = {
    "email": "aravind.m@gndsolutions.in",
    "authMethod": "PASSWORD",
    "password": EXPECTED_HASH,
    "remember_me": True
}
print("\n--- Manual Payload ---")
print(f"Same as conftest? {manual_payload == LOGIN_PAYLOAD}")
resp2 = requests.post("https://authentication.thinxview.com/api/auth/login/", json=manual_payload, verify=False)
print(f"Manual Request Status: {resp2.status_code}")

