import requests
import hashlib
import urllib3
import sys
urllib3.disable_warnings()

# Set stdout/stderr to utf-8 explicitly
sys.stdout.reconfigure(encoding='utf-8')

# P@sswørd123
passwords = ["Aravind@123", "Aravind@1234", "P@sswørd123", "P@ssw\u00F8rd123"]

url = "https://authentication.thinxview.com/api/auth/login/"

found = False
for pwd in passwords:
    h = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
    try:
        # Try with isSuperAdmin: False
        json_data = {
            "email": "aravind.m@gndsolutions.in", 
            "authMethod": "PASSWORD", 
            "password": h, 
            "remember_me": True,
            "isSuperAdmin": False
        }
        r = requests.post(url, json=json_data, verify=False, timeout=10)
        
        if r.status_code == 200:
            print(f"SUCCESS with isSuperAdmin=False! Password: '{pwd}'")
            found = True
            break
        else:
            print(f"Failed '{pwd}' with isSuperAdmin=False: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"Error checking '{pwd}': {e}")
        
if not found:
    print("ALL PASSWORDS FAILED")
