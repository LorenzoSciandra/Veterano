"""Unico punto che chiama il modello (Vercel AI Gateway, endpoint OpenAI-compatibile).

- Chiave solo da variabile d'ambiente AI_GATEWAY_API_KEY (mai scritta su file).
- VETERANO_OFFLINE=1 -> nessuna chiamata: i chiamanti usano il percorso deterministico/fixture.
- Ogni output JSON viene validato con pydantic; se non è valido si solleva LLMError e il chiamante ripiega.
"""
from __future__ import annotations

import json
import os
import re
from typing import TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

BASE_URL = "https://ai-gateway.vercel.sh/v1"
TIMEOUT_S = 20

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


def offline() -> bool:
    return os.getenv("VETERANO_OFFLINE", "0") == "1" or not os.getenv("AI_GATEWAY_API_KEY")


def mode() -> str:
    return "offline" if offline() else "live"


def model_id() -> str:
    return os.getenv("VETERANO_MODEL", "anthropic/claude-haiku-5.5")


_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(api_key=os.environ["AI_GATEWAY_API_KEY"], base_url=BASE_URL, timeout=TIMEOUT_S, max_retries=1)
    return _client


# Il modello spende token di ragionamento prima del testo: sotto ~1000 token la risposta può
# arrivare vuota con finish_reason="length" (verificato 14/11: 150 token -> 150 di ragionamento, testo "").
MIN_TOKENS = 1200


def chat_text(system: str, user: str, max_tokens: int = 400) -> str:
    if offline():
        raise LLMError("offline")
    try:
        r = _get_client().chat.completions.create(
            model=model_id(),
            max_tokens=max(max_tokens, MIN_TOKENS),
            temperature=0,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
    except Exception as e:  # rete, 401, 402 credito finito, timeout
        raise LLMError(f"{type(e).__name__}: {e}") from e
    text = (r.choices[0].message.content or "").strip()
    if not text:
        raise LLMError(f"risposta vuota (finish_reason={r.choices[0].finish_reason})")
    return text


_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def chat_json(system: str, user: str, schema: type[T], max_tokens: int = 800) -> T:
    raw = chat_text(system + "\n\nRispondi SOLO con un oggetto JSON valido, senza testo prima o dopo.", user, max_tokens)
    m = _JSON_BLOCK.search(raw)
    if not m:
        raise LLMError(f"nessun JSON nella risposta: {raw[:200]!r}")
    try:
        return schema.model_validate(json.loads(m.group(0)))
    except (json.JSONDecodeError, ValidationError) as e:
        raise LLMError(f"JSON non valido: {e}") from e
