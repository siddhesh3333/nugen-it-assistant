"""List aligned models and clearly identify those available for inference."""

from pathlib import Path
import os
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from services.nugen_client import NugenAPIError, list_aligned_models  # noqa: E402

api_key = os.getenv("NUGEN_API_KEY", "").strip()
base_url = os.getenv("NUGEN_API_BASE_URL", "https://api.nugen.in/api/v3")

try:
    models = list_aligned_models(api_key, base_url)
except NugenAPIError as exc:
    print(f"ERROR: {exc}")
    raise SystemExit(1)

if not models:
    print("Nugen returned no aligned models for this API key.")
    raise SystemExit(0)

print(f"Found {len(models)} aligned model(s):\n")
for index, model in enumerate(models, start=1):
    model_id = model.get("model_id", "<missing model_id>")
    name = model.get("model_name", "<unnamed>")
    base = model.get("base_model_id", "<unknown base model>")
    status = str(model.get("deployment_status", "UNKNOWN")).upper()
    print(f"{index}. {name}")
    print(f"   Status:   {status}")
    print(f"   Base:     {base}")
    print(f"   Model ID: {model_id}")
    print()

ready = [m for m in models if str(m.get("deployment_status", "")).upper() == "DEPLOYED"]
print(f"Deployed models available for inference: {len(ready)}")
