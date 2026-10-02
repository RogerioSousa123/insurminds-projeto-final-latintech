$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Ambiente virtual não encontrado. Execute: python -m venv .venv"
}
& ".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8505 --server.headless true --browser.gatherUsageStats false
