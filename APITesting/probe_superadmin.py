
import requests
import hashlib
import urllib3
import json

urllib3.disable_warnings()

URL = "https://authentication.thinxview.com/api/auth/login/"

def check():
    pwd = "Aravind@123"
    h = hashlib.sha256(pwd.encode()).hexdigest()
    payload = {
        "email": "aravind.m@gndsolutions.in",
        "authMethod": "PASSWORD",
        "password": h,
        "remember_me": True,
        "isSuperAdmin": False
    }
    print(f"Testing payload: {payload}")
    try:
        resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
