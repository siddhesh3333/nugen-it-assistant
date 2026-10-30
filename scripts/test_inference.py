"""Send one inexpensive smoke-test request to a deployed aligned model."""

from pathlib import Path
import os
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from services.nugen_client import (  # noqa: E402
    NugenAPIError,
    chat_completion,
    list_aligned_models,
)

api_key = os.getenv("NUGEN_API_KEY", "").strip()
base_url = os.getenv("NUGEN_API_BASE_URL", "https://api.nugen.in/api/v3")
requested_id = os.getenv("NUGEN_MODEL_ID", "").strip()

try:
    models = list_aligned_models(api_key, base_url)
    deployed = [
        model for model in models
        if str(model.get("deployment_status", "")).upper() == "DEPLOYED"
    ]

    if requested_id:
        selected = next((m for m in deployed if m.get("model_id") == requested_id), None)
        if selected is None:
            available = ", ".join(str(m.get("model_id")) for m in deployed) or "none"
            raise NugenAPIError(
                f"NUGEN_MODEL_ID is not in the deployed-model list for this API key. "
                f"Deployed IDs: {available}. Update .env with an exact ID from list_models.py."
            )
    else:
        qwen_matches = [
            m for m in deployed
            if "qwen/qwen2.5-1.5b-instruct" in str(m.get("base_model_id", "")).lower()
        ]
        candidates = qwen_matches or deployed
        if not candidates:
            raise NugenAPIError(
                "No DEPLOYED aligned models were returned. Deploy a model in Nugen first."
            )
        selected = candidates[0]

    model_id = str(selected["model_id"])
    print("Using model:", selected.get("model_name"))
    print("Base model:", selected.get("base_model_id"))
    print("Model ID:", model_id)

    result = chat_completion(
        api_key=api_key,
        model_id=model_id,
        api_base_url=base_url,
        max_tokens=180,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the Northsas Example Company IT Support Assistant. "
                    "Use only information supported by the IT support knowledge learned "
                    "during domain alignment. Do not invent policies, contact details, "
                    "or procedures. If the information is not available, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": (
                    "What should an employee do if they forget their account password? "
                    "Only state steps supported by the Northsas support guidance."
                ),
            },
        ],
    )

    print("\nINFERENCE SUCCEEDED")
    print("Answer:\n")
    print(result["answer_text"])
    print("\nConfidence score:", result.get("confidence_score", "not returned"))
    print("Usage:", result.get("usage", "not returned"))

except NugenAPIError as exc:
    print(f"INFERENCE FAILED: {exc}")
    raise SystemExit(1)
