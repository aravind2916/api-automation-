
import pytest
import requests
import hashlib
import json
import urllib3

urllib3.disable_warnings()

def test_debug_login_direct():
    URL = "https://authentication.thinxview.com/api/auth/login/"
    EMAIL = "aravind.m@gndsolutions.in"
    PWD = "Aravind@123"
    PWD_HASH = "dfaa43cb4002f53d61e9a36b3353bd79820f42337a7adccdce69d04fc076"
    
    payload = {
        "email": EMAIL,
        "password": PWD_HASH,
        "authMethod": "PASSWORD",
    
    resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"}, verify=False)
    
    with open("debug_real_output.txt", "w") as f:
        f.write(f"Payload: {payload}\n")
        f.write(f"Status: {resp.status_code}\n")
        f.write(f"Response: {resp.text}\n")
    
    assert resp.status_code == 200
