@echo off
cd /d "%~dp0.."
"ecommerce_analytics_app\venv\Scripts\python.exe" "scripts\ml_analyzer.py" %1 %2
