# main.py
import os
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
# Lee el manifiesto de la flota para saber cuál es el agente raíz
FLEET_YAML_PATH = os.path.join(AGENTS_DIR, "fleet.yaml")

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    fleet_yaml_path=FLEET_YAML_PATH
)

@app.get("/health")
def health_check():
    return {"status": "ok"} 