import pytest
import requests

@pytest.fixture(scope="session")
def api_client():
    """Session client for all API calls."""
    session = requests.Session()
    return session
