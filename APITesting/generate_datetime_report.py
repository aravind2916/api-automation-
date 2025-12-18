import os
import sys
import pytest
import xml.etree.ElementTree as ET
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import json

# Configuration
TEST_PATH = "tests/test_update_datetime_format_ddt.py"
REPORT_XML = "reports/datetime_results.xml"
REPORT_HTML = "reports/datetime_update_report.html"
TEMPLATE_DIR = "templates"
DATA_FILE = "data/update_datetime_format_testdata.json"

def run_tests():
    """Run pytest and generate XML report"""
    print(f"Running tests: {TEST_PATH}...")
    args = [
        "-v", 
        TEST_PATH, 
        f"--junitxml={REPORT_XML}",
        "-o", "junit_family=xunit2" # Ensure standard format
    ]
    pytest.main(args)

def load_test_data():
    """Load DDT cases from JSON (Handling valid/invalid lists)"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            flat_cases = {}
            # Flatten "valid_cases" and "invalid_cases"
            for category in ["valid_cases", "invalid_cases"]:
                for case in data.get(category, []):
                    # Use "title" as the key, as pytest implementation uses ids=[c["title"]...]
                    flat_cases[case["title"]] = case
            
            return flat_cases
    except Exception as e:
        print(f"Warning: Could not load test data: {e}")
        return {}

def parse_xml_results(xml_path):
    """Parse JUnit XML into a structured dict for Jinja2"""
    # Load DDT data first
    ddt_data = load_test_data()
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Root suite stats (pytest usually puts one testsuite)
    testsuite = root.find("testsuite")
    if testsuite is None:
        # Sometimes multiple suites, or root IS the suite
        testsuite = root
    
    stats = {
        "total": int(testsuite.get("tests", 0)),
        "failed": int(testsuite.get("failures", 0)) + int(testsuite.get("errors", 0)),
        "skipped": int(testsuite.get("skipped", 0)),
        "duration": float(testsuite.get("time", 0)),
        "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    stats["passed"] = stats["total"] - stats["failed"] - stats["skipped"]
    stats["passed_percent"] = round((stats["passed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
    
    tests = []
    for case in testsuite.findall("testcase"):
        # Basic info
        name = case.get("name") # e.g. test_update_datetime_format_valid_cases[MM/DD/YYYY + USER_LOCAL]
        classname = case.get("classname")
        time = case.get("time")
        
        # Extract the parameter ID from the name
        # pytest name format: function_name[param_id]
        param_id = ""
        if "[" in name and name.endswith("]"):
            start = name.find("[") + 1
            param_id = name[start:-1]
        
        # Lookup extra data from JSON using param_id (which corresponds to title)
        raw_data = ddt_data.get(param_id, {})
        
        # Determine outcome
        outcome = "passed"
        longrepr = ""
        
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        
        if failure is not None:
            outcome = "failed"
            longrepr = failure.text
        elif error is not None:
            outcome = "failed" 
            longrepr = error.text
        elif skipped is not None:
            outcome = "skipped"
            longrepr = skipped.get("message", "")
        
        # Extract short error message (The "English description")
        short_message = ""
        if longrepr:
            # Find lines starting with "E   " (pytest standard)
            lines = [line.strip() for line in longrepr.split('\n') if line.strip().startswith("E ")]
            if lines:
                # Clean up the "E   " prefix
                short_message = "\n".join([l[2:].strip() for l in lines])
            else:
                # Fallback: Just take the last line if no E lines found
                lines = [l for l in longrepr.split('\n') if l.strip()]
                if lines:
                    short_message = lines[-1]

        # Try to capture stdout/stderr (system-out/system-err)
        stdout = case.find("system-out")
        stderr = case.find("system-err")
        
        tests.append({
            "name": name,
            "display_name": param_id if param_id else name,
            "nodeid": f"{classname}::{name}",
            "location": f"{case.get('file')}:{case.get('line')}",
            "duration": time,
            "outcome": outcome,
            "longrepr": longrepr,
            "short_message": short_message, 
            "stdout": stdout.text if stdout is not None else "",
            "stderr": stderr.text if stderr is not None else "",
            # Enhanced Data
            "payload": json.dumps(raw_data.get("payload"), indent=2) if raw_data.get("payload") else None,
            "expected_status": raw_data.get("expected_status"),
            "description": raw_data.get("title", raw_data.get("description", "")) 
        })
        
    return stats, tests

def generate_html(stats, tests):
    """Render the Jinja2 template"""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    # Reuse the same premium template
    template = env.get_template("dashboard_book.html")
    
    html_content = template.render(
        tests=tests,
        report_title="DateTime Update Test Report", 
        **stats
    )
    
    with open(REPORT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\nReport generated successfully: {os.path.abspath(REPORT_HTML)}")

if __name__ == "__main__":
    # Ensure reports dir exists
    os.makedirs("reports", exist_ok=True)
    
    # 1. Run Tests
    run_tests()
    
    # 2. Parse Results
    if os.path.exists(REPORT_XML):
        stats, tests = parse_xml_results(REPORT_XML)
        
        # 3. Generate HTML
        generate_html(stats, tests)
    else:
        print("Error: No XML report found. Tests might have crashed completely.")
