"""Northstar IT Support Assistant powered by a deployed Nugen aligned model."""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from services.nugen_client import NugenAPIError, chat_completion, list_aligned_models


# Load the .env located beside app.py, regardless of terminal working directory.
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

API_KEY = os.getenv("NUGEN_API_KEY", "").strip()
API_BASE_URL = os.getenv("NUGEN_API_BASE_URL", "https://api.nugen.in/api/v3").strip()
DEFAULT_MODEL_ID = os.getenv("NUGEN_MODEL_ID", "").strip()

SYSTEM_PROMPT = """You are the Northstar Example Company IT Support Assistant.

Help employees with account access, password support, VPN, devices, software,
and IT service tickets.

Important rules:
1. Answer only with information supported by the IT support knowledge learned
   during domain alignment.
2. Do not invent company policies, phone numbers, email addresses, approval
   workflows, identity-verification steps, or troubleshooting procedures.
3. If the provided knowledge does not specify an answer, say that clearly.
4. For security-sensitive matters, never ask the user to share a password,
   one-time code, recovery code, or secret credential in chat.
5. If the question is ambiguous, ask one concise clarification question.
6. Be practical, clear, and concise. Use numbered steps when appropriate.

Do not claim that you searched a live company knowledge base. This application
uses the deployed domain-aligned model; it does not retrieve document passages
at query time.
"""


st.set_page_config(
    page_title="Northstar IT Support Assistant",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Northstar IT Support Assistant")
st.caption("An IT help assistant powered by your deployed Nugen domain-aligned model.")

with st.sidebar:
    st.header("Model settings")
    st.write("The app checks your Nugen account for aligned models that are marked DEPLOYED.")

    if not API_KEY:
        st.error("NUGEN_API_KEY is missing. Create a .env file beside app.py.")
        st.stop()

    if st.button("Refresh deployed models", use_container_width=True):
        st.session_state.pop("nugen_models", None)
        st.session_state.pop("selected_model_id", None)

    if "nugen_models" not in st.session_state:
        with st.spinner("Loading deployed models from Nugen..."):
            try:
                all_models = list_aligned_models(API_KEY, API_BASE_URL)
                st.session_state.nugen_models = [
                    model for model in all_models
                    if str(model.get("deployment_status", "")).upper() == "DEPLOYED"
                    and model.get("model_id")
                ]
            except NugenAPIError as exc:
                st.error(str(exc))
                st.stop()

    deployed_models = st.session_state.nugen_models
    if not deployed_models:
        st.warning(
            "No DEPLOYED aligned models were returned for this API key. "
            "Confirm the model is deployed and that this key belongs to the same Nugen account."
        )
        st.stop()

    def model_label(model: dict) -> str:
        return (
            f"{model.get('model_name', 'Unnamed model')} | "
            f"{model.get('base_model_id', 'unknown base')}"
        )

    preferred_index = 0
    if DEFAULT_MODEL_ID:
        for idx, model in enumerate(deployed_models):
            if model.get("model_id") == DEFAULT_MODEL_ID:
                preferred_index = idx
                break
    else:
        for idx, model in enumerate(deployed_models):
            if "qwen/qwen2.5-1.5b-instruct" in str(model.get("base_model_id", "")).lower():
                preferred_index = idx
                break

    models_by_id = {str(model["model_id"]): model for model in deployed_models}
    model_ids = list(models_by_id.keys())
    selected_model_id = st.selectbox(
        "Select deployed aligned model",
        options=model_ids,
        index=preferred_index,
        format_func=lambda model_id: model_label(models_by_id[model_id]),
    )
    selected_model = models_by_id[selected_model_id]
    st.session_state.selected_model_id = selected_model_id
    st.caption(f"Model ID: `{selected_model_id}`")
    st.caption(f"Deployment: {selected_model.get('deployment_status', 'DEPLOYED')}")

    st.divider()
    st.subheader("How to use")
    st.markdown(
        "Ask a question about the Northstar IT support guidance. "
        "Do not enter passwords, OTPs, or other secrets."
    )
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_usage = None
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_usage" not in st.session_state:
    st.session_state.last_usage = None

# Display the conversation already held in this Streamlit session.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask an IT support question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Keep recent context to reduce unnecessary prompt growth.
    recent_history = st.session_state.messages[-12:]
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + recent_history

    with st.chat_message("assistant"):
        with st.spinner("Asking your deployed Nugen model..."):
            try:
                result = chat_completion(
                    api_key=API_KEY,
                    model_id=selected_model_id,
                    messages=api_messages,
                    api_base_url=API_BASE_URL,
                    max_tokens=450,
                    temperature=0.2,
                )
                answer = str(result.get("answer_text", "")).strip()
                if not answer:
                    answer = "The model returned an empty response. Please try again."
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.session_state.last_usage = {
                    "confidence_score": result.get("confidence_score"),
                    "usage": result.get("usage"),
                    "model": result.get("model"),
                }
            except NugenAPIError as exc:
                st.error(str(exc))
                # Keep the failed user prompt visible, but do not add a fake answer.

if st.session_state.last_usage:
    usage = st.session_state.last_usage
    with st.expander("Last response details"):
        st.write("Model:", usage.get("model"))
        if usage.get("confidence_score") is not None:
            st.write("Nugen confidence score:", usage["confidence_score"])
        st.write("Token usage:", usage.get("usage"))

if st.session_state.messages:
    export_data = {
        "application": "Northstar IT Support Assistant",
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": st.session_state.get("selected_model_id"),
        "messages": st.session_state.messages,
    }
    st.download_button(
        "Download conversation (JSON)",
        data=json.dumps(export_data, indent=2, ensure_ascii=False),
        file_name="northstar_it_support_conversation.json",
        mime="application/json",
    )

st.divider()
st.caption(
    "Important: model alignment is not the same as retrieval-augmented generation. "
    "Check policy-specific answers against the original Northstar documents before relying on them."
)
