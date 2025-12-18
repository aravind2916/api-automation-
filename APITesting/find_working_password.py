import requests
import hashlib
import urllib3
urllib3.disable_warnings()

# Test BOTH passwords to find which one works RIGHT NOW
passwords = ["Aravind@123", "Aravind@1234"]

for pwd in passwords:
    h = hashlib.sha256(pwd.encode()).hexdigest()
    try:
        r = requests.post(
            "https://authentication.thinxview.com/api/auth/login/",
            json={"email": "aravind.m@gndsolutions.in", "authMethod": "PASSWORD", "password": h, "remember_me": True},
            verify=False,
            timeout=10
        )
        if r.status_code == 200:
            print(f"WORKING PASSWORD: {pwd}")
            print(f"Hash: {h}")
            break
        else:
            print(f"{pwd}: FAILED (Status {r.status_code})")
    except Exception as e:
        print(f"{pwd}: ERROR - {e}")
