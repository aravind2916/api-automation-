import requests
import hashlib
import urllib3
import pytest
import json

urllib3.disable_warnings()

urllib3.disable_warnings()

@pytest.fixture(scope="session")
def auth_token():
    """
    Obtain auth token with self-healing logic.
    If default login fails, it tries known passwords, resets to default, and retries.
    """
    login_url = "https://authentication.thinxview.com/api/auth/login/"
    reset_url = "https://r2xywlbqc9.execute-api.ap-south-1.amazonaws.com/api/profile/aravind.m@gndsolutions.in/thinxfresh/update-password"
    
    default_pwd = "Aravind@123"
    # List of passwords used in tests to try if default fails
    known_passwords = [
        default_pwd,
        "Aravind@1234",      # New from rescue
        "Aravind@12345",
        "ThinxView@2025",
        "P@ssw\u00F8rd123",  # unicode escaped
        "P@sswørd123",       # literal
        "P@sswrd123",        # missing char variant
        "LongPassword123!@#$%",
        "Pa$$w0rd!",
        "Valid123!",
    ]

    def try_login(password):
        pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        try:
            r = requests.post(
                login_url,
                json={
                    "email": "aravind.m@gndsolutions.in",
                    "authMethod": "PASSWORD",
                    "password": pwd_hash,
                    "remember_me": True,
                    "isSuperAdmin": False
                },
                headers={"Content-Type": "application/json"},
                verify=False,
                timeout=10
            )
            if r.status_code == 200:
                return r.json().get("token")
            print(f"DEBUG: Login failed for '{password}'. Status: {r.status_code}, Body: {r.text}")
            return None
        except Exception as e:
            print(f"DEBUG: Exception during login for '{password}': {e}")
            return None

    # 1. Try default password first
    print(f"DEBUG: Trying default password '{default_pwd}'...")
    token_str = try_login(default_pwd)
    
    if token_str:
        return json.dumps(token_str)

    # 2. If failed, try rescue
    print("DEBUG: Default login failed. Attempting rescue with known passwords...")
    found_pwd = None
    rescue_token = None

    for pwd in known_passwords:
        if pwd == default_pwd: continue
        print(f"DEBUG: Trying candidate '{pwd}'...")
        t = try_login(pwd)
        if t:
            print(f"DEBUG: Found working password: '{pwd}'")
            found_pwd = pwd
            rescue_token = t
            break
    
    if not rescue_token:
        raise RuntimeError(f"FATAL: Could not login with any known password. Please manually reset account.")

    # 3. Reset to default
    print(f"DEBUG: Resetting password from '{found_pwd}' to '{default_pwd}'...")
    try:
        rr = requests.put(
            reset_url,
            headers={
                "Authorization": f"Bearer {json.dumps(rescue_token)}",
                "Content-Type": "application/json"
            },
            json={"newPassword": default_pwd, "confirmPassword": default_pwd},
            verify=False,
            timeout=10
        )
        if rr.status_code == 200:
             print("DEBUG: Password reset successful.")
        else:
             # Even if reset fails (e.g. same password?), we have a working token, 
             # but we should warn.
             print(f"WARNING: Password reset failed: {rr.status_code} {rr.text}")
    except Exception as e:
        print(f"WARNING: Password reset exception: {e}")

    # 4. Return the token (either the rescue one, or a new one)
    # Since we changed password, the old token might still be valid or we need a new one.
    # Safe bet: get a NEW token with the default password.
    final_token = try_login(default_pwd)
    if not final_token:
        # If reset worked but we can't login, fallback to rescue_token (if it still works)
        if rr.status_code == 200:
             raise RuntimeError("Reset appeared successful but subsequent login failed.")
        return json.dumps(rescue_token)
        
    return json.dumps(final_token)


def pytest_html_report_title(report):
    report.title = "ThinxView API Test Dashboard"

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        "<h1>ThinxView API Test Automation</h1>",
        "<p>Detailed execution results for Update Temperature Unit API.</p>"
    ])

def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Description</th>")
    cells.insert(3, "<th>Test Data</th>")

def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{getattr(report, 'description', '')}</td>")
    cells.insert(3, f"<td>{getattr(report, 'test_data', '')}</td>")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # Extract test description from parameterized data
    if hasattr(item, 'callspec'):
        data = item.callspec.params.get('data')
        if data:
             report.description = data.get('testcase', 'N/A')
             report.test_data = json.dumps(data.get('payload', {}), indent=2)


