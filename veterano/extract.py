"""Racconto dell'esperto -> segmenti con ID -> bozza di scheda.

Il modello propone i campi citando gli ID dei segmenti. Un controllo deterministico poi
scarta ogni campo che cita segmenti inesistenti o nessun segmento: un campo senza fonte resta mancante.
"""
from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel

from . import llm
from .models import Card, FieldName, FieldValue, Segment
from .rules import normalize


def split_segments(story: str, source_id: str, expert: str, start: int = 1) -> list[Segment]:
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", story) if p.strip()]
    now = datetime.now()
    return [
        Segment(segment_id=f"{source_id}#{start + i}", source_id=source_id, expert=expert, text=p, recorded_at=now)
        for i, p in enumerate(parts)
    ]


class _FieldOut(BaseModel):
    value: str | None = None
    segment_ids: list[str] = []


class _CardOut(BaseModel):
    task_id: str
    context: _FieldOut
    action: _FieldOut
    rationale: _FieldOut


EXTRACT_SYSTEM = """Sei l'estrattore del Veterano, una memoria di reparto industriale.
Dal racconto di un tecnico, diviso in segmenti con ID, estrai UNA scheda con:
- task_id: compito, in forma "P17-controllo-visivo" (codice pezzo senza trattino + compito in minuscolo con trattini). Se il compito è tra quelli noti, usa esattamente quell'ID.
- context: variante o condizione in cui vale (es. "P-17 variante A"). Se il racconto non la dice esplicitamente, value = null.
- action: cosa fa il tecnico, riformulato in modo operativo e breve.
- rationale: perché lo fa (quale errore evita o quale esito fa riconoscere). Se non è detto esplicitamente, value = null.
Per ogni campo con valore, segment_ids elenca gli ID dei segmenti che lo sostengono.
REGOLA: non dedurre e non completare. Se un'informazione non è scritta nel racconto, value = null e segment_ids = [].
Formato: {"task_id": str, "context": {"value": str|null, "segment_ids": [str]}, "action": {...}, "rationale": {...}}"""


def _guard(fo: _FieldOut, valid_ids: set[str]) -> FieldValue:
    ids = [i for i in fo.segment_ids if i in valid_ids]
    if not fo.value or not ids:
        return FieldValue()
    return FieldValue(value=fo.value.strip(), segment_ids=ids)


def _offline_extract(segments: list[Segment]) -> _CardOut:
    """Percorso deterministico dichiarato: azione = primo segmento, contesto e motivazione mancanti."""
    first = segments[0]
    m = re.search(r"\bP-?\s?(\d+)", first.text, re.IGNORECASE)
    task = f"P{m.group(1)}-da-classificare" if m else "compito-da-classificare"
    return _CardOut(
        task_id=task,
        context=_FieldOut(),
        action=_FieldOut(value=first.text, segment_ids=[first.segment_id]),
        rationale=_FieldOut(),
    )


def extract_card(
    story: str, expert: str, source_id: str, card_id: str, known_tasks: list[str]
) -> tuple[Card, list[Segment], str]:
    """Restituisce (bozza, segmenti, modalità usata: live|offline|fallback)."""
    segments = split_segments(story, source_id, expert)
    if not segments:
        raise ValueError("Racconto vuoto")
    used = "offline"
    out: _CardOut
    if not llm.offline():
        listing = "\n".join(f"[{s.segment_id}] {s.text}" for s in segments)
        user = f"Compiti noti: {', '.join(known_tasks) or 'nessuno'}\n\nSegmenti:\n{listing}"
        try:
            out = llm.chat_json(EXTRACT_SYSTEM, user, _CardOut)
            used = "live"
        except llm.LLMError:
            out = _offline_extract(segments)
            used = "fallback"
    else:
        out = _offline_extract(segments)

    valid = {s.segment_id for s in segments}
    card = Card(
        card_id=card_id,
        version=1,
        status="bozza",
        task_id=out.task_id.strip(),
        context=_guard(out.context, valid),
        action=_guard(out.action, valid),
        rationale=_guard(out.rationale, valid),
        expert=expert,
    )
    card.missing_fields = card.computed_missing()
    return card, segments, used


class _ValueOut(BaseModel):
    value: str | None = None


NORMALIZE_SYSTEM = """Sei il Veterano. Un tecnico ha risposto a una domanda su un campo di una scheda.
Restituisci il valore del campo in forma breve e canonica, usando SOLO ciò che il tecnico ha detto.
- Campo "context": la variante o condizione, nel formato "<pezzo> variante <lettera>" o "<pezzo> <condizione>" (es. "P-17 variante A").
- Campo "rationale": una frase che dice quale errore evita o quale esito fa riconoscere.
Se la risposta non contiene l'informazione, value = null. Formato: {"value": str|null}"""


def propose_value(field: FieldName, answer: str, card: Card) -> tuple[str | None, str]:
    """Propone il valore canonico del campo dalla risposta dell'esperto. Il responsabile può correggerlo."""
    if not llm.offline():
        user = f"Campo: {field}\nCompito: {card.task_id}\nAzione: {card.action.value}\nRisposta del tecnico: {answer}"
        try:
            return llm.chat_json(NORMALIZE_SYSTEM, user, _ValueOut, max_tokens=150).value, "live"
        except llm.LLMError:
            pass
    return _offline_value(field, answer, card), "offline"


def _offline_value(field: FieldName, answer: str, card: Card) -> str | None:
    if field == "context":
        m = re.search(r"variante\s+([A-Z])\b", answer, re.IGNORECASE)
        p = re.match(r"P(\d+)", card.task_id)
        if m and p:
            return f"P-{p.group(1)} variante {m.group(1).upper()}"
        return None
    return answer.strip() or None


def same_context(a: str | None, b: str | None) -> bool:
    return bool(a and b) and normalize(a) == normalize(b)
