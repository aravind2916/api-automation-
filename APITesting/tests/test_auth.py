import requests
import hashlib

LOGIN_URL = "https://authentication.thinxview.com/api/auth/login/"

def login_and_get_token_object():
    password = "Aravind@123"
    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    payload = {
        "email": "aravind.m@gndsolutions.in",
        "authMethod": "PASSWORD",
        "password": pwd_hash,
        "remember_me": True,
        "isSuperAdmin": False
    }

    response = requests.post(
        LOGIN_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
        verify=False
    )

    print("LOGIN status:", response.status_code)
    print("LOGIN body:", response.text)

    assert response.status_code == 200, "Login failed"

    data = response.json()
    return data["token"]
