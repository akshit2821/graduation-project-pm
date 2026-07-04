"""
Groq / OpenAI-compatible LLM client for Graduation-Project.

Loads env from shared Milestone 1 `.env` by default:
  E:\\PM Fellowship\\Project-cursor\\Milestone 1\\.env

Override with GRADUATION_ENV_FILE or MILESTONE_2_ENV_FILE.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = REPO_ROOT.parent / "Milestone 1" / ".env"

_env_loaded = False


def _parse_dotenv_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, _, val = line.partition("=")
    key, val = key.strip(), val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1]
    return (key, val) if key else None


def env_file_path() -> Path:
    for var in ("GRADUATION_ENV_FILE", "MILESTONE_2_ENV_FILE"):
        custom = os.environ.get(var, "").strip()
        if custom:
            return Path(custom)
    return DEFAULT_ENV_FILE


def load_env_file() -> None:
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    path = env_file_path()
    if not path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(path, override=False)
        return
    except ImportError:
        pass
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in raw.splitlines():
        parsed = _parse_dotenv_line(line)
        if parsed:
            k, v = parsed
            if k not in os.environ:
                os.environ[k] = v


def normalize_openai_base(url: str) -> str:
    u = (url or "").strip().rstrip("/")
    for suffix in ("/chat/completions", "/v1/chat/completions"):
        if u.endswith(suffix):
            u = u[: -len(suffix)].rstrip("/")
    return u


def get_llm_api_key() -> str:
    load_env_file()
    return (os.environ.get("LLM_API_KEY") or "").strip()


def get_llm_base_url() -> str:
    load_env_file()
    raw = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    return normalize_openai_base(raw)


def get_llm_model() -> str:
    load_env_file()
    return (os.environ.get("LLM_MODEL") or "llama-3.1-8b-instant").strip()


def get_llm_timeout() -> int:
    load_env_file()
    try:
        return int(os.environ.get("LLM_TIMEOUT_SECONDS", "60"))
    except ValueError:
        return 60


def llm_mode() -> str:
    load_env_file()
    return (os.environ.get("LLM_MODE") or "api").strip().lower()


def api_enabled(force: bool = False) -> bool:
    if not get_llm_api_key():
        return False
    if force:
        return True
    mode = llm_mode()
    return mode not in ("deterministic", "stub", "offline")


def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    force_api: bool = False,
) -> str:
    if not api_enabled(force=force_api):
        raise RuntimeError(
            "Groq API not enabled. Set LLM_API_KEY in Milestone 1/.env and LLM_MODE=api."
        )
    url = f"{get_llm_base_url()}/chat/completions"
    body = {
        "model": get_llm_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_llm_api_key()}",
            "User-Agent": "Graduation-Project/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=get_llm_timeout()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Groq API HTTP {e.code}: {err}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Groq API network error: {e}") from e

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"Groq API empty choices: {data}")
    return (choices[0].get("message") or {}).get("content") or ""
