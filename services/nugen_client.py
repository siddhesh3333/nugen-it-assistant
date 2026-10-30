"""Small, defensive client for Nugen's aligned-model inference API."""

from __future__ import annotations

from typing import Any

import requests


class NugenAPIError(RuntimeError):
    """An HTTP or response-format error returned by the Nugen API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _headers(api_key: str) -> dict[str, str]:
    if not api_key or not api_key.strip():
        raise NugenAPIError("NUGEN_API_KEY is empty. Add it to your .env file.")
    return {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def list_aligned_models(
    api_key: str,
    api_base_url: str = "https://api.nugen.in/api/v3",
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return aligned models visible to the authenticated Nugen account."""
    url = f"{api_base_url.rstrip('/')}/models/aligned"
    try:
        response = requests.get(
            url,
            headers=_headers(api_key),
            params={"limit": limit},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise NugenAPIError(f"Could not reach Nugen model list: {exc}") from exc

    if not response.ok:
        raise NugenAPIError(
            f"Model-list request failed (HTTP {response.status_code}): "
            f"{response.text[:1500]}",
            response.status_code,
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise NugenAPIError("Nugen returned a non-JSON model-list response.") from exc

    models = data.get("domain_aligned_models", [])
    if not isinstance(models, list):
        raise NugenAPIError(
            "Unexpected response from Nugen: 'domain_aligned_models' is not a list."
        )
    return models


def chat_completion(
    api_key: str,
    model_id: str,
    messages: list[dict[str, str]],
    api_base_url: str = "https://api.nugen.in/api/v3",
    max_tokens: int = 450,
    temperature: float = 0.2,
) -> dict[str, Any]:
    """Send a non-streaming chat completion request to an aligned model."""
    if not model_id or not model_id.strip():
        raise NugenAPIError("No model ID supplied. Select a deployed aligned model first.")

    url = f"{api_base_url.rstrip('/')}/inference/chat/completions"
    payload = {
        "model": model_id.strip(),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        response = requests.post(
            url,
            headers=_headers(api_key),
            json=payload,
            timeout=120,
        )
    except requests.Timeout as exc:
        raise NugenAPIError(
            "Nugen inference timed out. Try again or reduce max_tokens."
        ) from exc
    except requests.RequestException as exc:
        raise NugenAPIError(f"Could not reach Nugen inference: {exc}") from exc

    if not response.ok:
        body = response.text[:2500]
        raise NugenAPIError(
            f"Inference failed (HTTP {response.status_code}): {body}",
            response.status_code,
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise NugenAPIError("Nugen returned a non-JSON inference response.") from exc

    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise NugenAPIError(
            f"Unexpected Nugen response format: {str(data)[:1500]}"
        ) from exc

    data["answer_text"] = answer
    return data
