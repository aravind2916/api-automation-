import json
import os

def load_test_data(filename):
    """
    Load test data from JSON file dynamically.
    Example: load_test_data("testdata_kpi.json")
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Go one level up from utils/
    file_path = os.path.join(base_dir, "data", filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Test data file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
