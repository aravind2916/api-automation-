import requests
from APITesting.utils.auth_token import get_token


def api_request(method: str, url: str, headers=None, **kwargs):
    if headers is None:
        headers = {}

    token = get_token()

    final_headers = {
        "Content-Type": "application/json",
        **headers,
        "Authorization": f"Bearer {token}",
    }

    return requests.request(
        method=method,
        url=url,
        headers=final_headers,
        verify=False,
        timeout=20,
        **kwargs,
    )
