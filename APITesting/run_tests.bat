@echo off
echo Clearing Python cache...
if exist __pycache__ rd /s /q __pycache__
if exist utils\__pycache__ rd /s /q utils\__pycache__
if exist tests\__pycache__ rd /s /q tests\__pycache__
if exist .pytest_cache rd /s /q .pytest_cache

echo Running tests...
python -m pytest tests\test_update_password_ddt.py -v --html=reports/password_update_report.html --self-contained-html
