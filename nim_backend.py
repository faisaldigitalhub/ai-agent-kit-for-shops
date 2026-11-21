"""Optional NVIDIA NIM backend for the AI Agent Kit for Shops.

This backend is OPTIONAL. The kit works fully offline without it, using
the rules engine in rules.py. This file only adds smarter, free-text
replies when the user has a key.

How the key is read:
    Only from the environment variable NVIDIA_API_KEY.
    Never from a file in this repo, never hardcoded, never logged.

How to get a free key:
    Create a free account at build.nvidia.com, open Settings -> API Keys,
    and generate a key. The free key is for prototyping, development and
    testing only, and it is rate-limited. Production use serving real
    customers needs an NVIDIA AI Enterprise licence.

If the key is missing, or the call fails for any reason, ask_nim returns
None and the agent falls back to the offline rules engine automatically.
"""

import json
import os
import urllib.error
import urllib.request

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"


def has_key():
    """True when an NVIDIA API key is set in the environment."""
    return bool(os.environ.get("NVIDIA_API_KEY"))


def ask_nim(messages, model=DEFAULT_MODEL, max_tokens=300, timeout=60):
    """Send a chat request to NVIDIA NIM. Return the reply text, or None.

    messages is a list of {"role": ..., "content": ...} dicts, in
    OpenAI chat format. Any failure (no key, network error, HTTP error,
    bad response) returns None instead of raising, so the caller can
    fall back to the rules engine.
    """
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        return None

    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode("utf-8")

    request = urllib.request.Request(ENDPOINT, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", "Bearer " + key)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, urllib.error.HTTPError,
            KeyError, IndexError, ValueError):
        return None
