@echo off
setlocal
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente virtual nao encontrado. Execute: python -m venv .venv
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py

