@echo off
echo Starting Multi-Agent Interaction Web UI...
echo.
echo Installing dependencies...
pip install fastapi uvicorn jinja2 python-multipart websockets -q
echo.
echo Starting server...
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║       Multi-Agent Interaction Web UI                  ║
echo ╠═══════════════════════════════════════════════════════╣
echo ║  访问: http://localhost:8000                          ║
echo ║  API: http://localhost:8000/docs                       ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
cd /d "%~dp0"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload