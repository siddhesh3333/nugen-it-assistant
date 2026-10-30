"""Run a small manual-review evaluation set and save responses to CSV.

This script does not claim to automatically score factual correctness.
Review each answer against the uploaded source documents and fill in the
review columns in evaluation/results.csv.
"""

from pathlib import Path
import json
import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from services.nugen_client import (  # noqa: E402
    NugenAPIError,
    chat_completion,
    list_aligned_models,
)

API_KEY = os.getenv("NUGEN_API_KEY", "").strip()
BASE_URL = os.getenv("NUGEN_API_BASE_URL", "https://api.nugen.in/api/v3")
MODEL_ID = os.getenv("NUGEN_MODEL_ID", "").strip()
SYSTEM_PROMPT = (
    "You are the Northstar Example Company IT Support Assistant. "
    "Answer using only information supported by the IT support knowledge "
    "learned during domain alignment. Do not invent company policies, "
    "phone numbers, email addresses, or procedures. If information is "
    "unavailable, clearly say that the provided guidance does not specify it."
)

try:
    models = list_aligned_models(API_KEY, BASE_URL)
    deployed = [
        m for m in models
        if str(m.get("deployment_status", "")).upper() == "DEPLOYED"
    ]
    if MODEL_ID:
        selected = next((m for m in deployed if m.get("model_id") == MODEL_ID), None)
        if selected is None:
            raise NugenAPIError(
                "NUGEN_MODEL_ID is not currently listed as DEPLOYED. "
                "Run python scripts/list_models.py and update .env."
            )
    else:
        qwen = [
            m for m in deployed
            if "qwen/qwen2.5-1.5b-instruct" in str(m.get("base_model_id", "")).lower()
        ]
        if not (qwen or deployed):
            raise NugenAPIError("No deployed aligned model found for this API key.")
        selected = (qwen or deployed)[0]

    model_id = str(selected["model_id"])
    print("Evaluating:", selected.get("model_name"), "|", model_id)

    questions_path = ROOT / "evaluation" / "test_questions.json"
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    rows = []

    for item in questions:
        print(f"Running {item['id']} ...")
        result = chat_completion(
            api_key=API_KEY,
            model_id=model_id,
            api_base_url=BASE_URL,
            max_tokens=350,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["question"]},
            ],
        )
        usage = result.get("usage") or {}
        rows.append({
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "answer": result.get("answer_text", ""),
            "confidence_score": result.get("confidence_score"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "policy_supported (fill manually)": "",
            "relevant (fill manually)": "",
            "unsupported_claims (fill manually)": "",
            "review_notes": "",
        })

    output_path = ROOT / "evaluation" / "results.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(rows)} responses to: {output_path}")
    print("Open the CSV and manually compare each answer with the source documents.")

except (NugenAPIError, requests.RequestException) as exc:  # noqa: F821
    print(f"EVALUATION FAILED: {exc}")
    raise SystemExit(1)
