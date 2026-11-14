"""Domanda del neoassunto -> (compito, contesto) -> R3 -> risposta dalle sole schede ammesse, oppure rifiuto motivato.

Il modello: (1) interpreta la domanda in compito+contesto, validato contro i compiti noti;
(2) formula la risposta usando SOLO le schede che la regola R3 ha ammesso.
Ogni domanda lascia una AnswerTrace con schede candidate, schede usate (ID e versione) ed esito.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel

from . import llm
from .models import AnswerTrace, Card
from .rules import REFUSAL_TEXT, applicable
from .store import Store

# Parole chiave -> suffisso del compito, per il percorso deterministico (offline o fallback).
_KEYWORDS = {
    "controllo-visivo": ("controll", "visiv", "superficie", "ispezion"),
    "serraggio": ("serr", "vit", "bullon", "flangia"),
    "sbavatura": ("sbav", "bava", "lima"),
}


class _Parsed(BaseModel):
    task_id: str | None = None
    context: str | None = None


PARSE_SYSTEM = """Sei il Veterano. Interpreta la domanda di un operatore in:
- task_id: uno ESATTAMENTE tra i compiti noti elencati, oppure null se nessuno corrisponde;
- context: la variante o condizione nominata nella domanda, in forma "<pezzo> variante <lettera>" (es. "P-17 variante A") o "<pezzo> <condizione>" (es. "P-22 lotto standard"); null se la domanda non la nomina.
Non indovinare la variante se non è scritta. Formato: {"task_id": str|null, "context": str|null}"""

ANSWER_SYSTEM = """Sei il Veterano, assistente di reparto. Rispondi in italiano, in 2-3 frasi operative,
usando SOLO le schede fornite. Non aggiungere passaggi, valori o avvertenze che non sono nelle schede.
Chiudi citando la scheda tra parentesi quadre, es. [CARD-P17-SER-01 v1]."""


def parse_offline(question: str, known_tasks: list[str], previous_task: str | None = None) -> _Parsed:
    q = question.lower()
    part_m = re.search(r"\bp-?\s?(\d+)", q)
    part = part_m.group(1) if part_m else None
    prev_part = re.match(r"P(\d+)-", previous_task).group(1) if previous_task and re.match(r"P(\d+)-", previous_task) else None
    if part is None:
        part = prev_part  # "E per la variante B?": il pezzo è quello della domanda precedente
    task = None
    if part:
        for suffix, words in _KEYWORDS.items():
            cand = f"P{part}-{suffix}"
            if cand in known_tasks and any(w in q for w in words):
                task = cand
                break
        if task is None and previous_task and part == prev_part:
            task = previous_task  # follow-up sullo stesso pezzo senza nominare il compito
    ctx = None
    if part:
        v = re.search(r"variante\s+([a-z])\b", q)
        if v:
            ctx = f"P-{part} variante {v.group(1).upper()}"
        elif "lotto standard" in q:
            ctx = f"P-{part} lotto standard"
    return _Parsed(task_id=task, context=ctx)


def parse_question(question: str, known_tasks: list[str], previous_task: str | None = None) -> tuple[_Parsed, str]:
    if not llm.offline():
        prev = f"\nCompito della domanda precedente (usalo se la domanda è un seguito e non nomina un altro compito): {previous_task}" if previous_task else ""
        try:
            p = llm.chat_json(PARSE_SYSTEM, f"Compiti noti: {', '.join(known_tasks)}{prev}\nDomanda: {question}", _Parsed)
            if p.task_id not in known_tasks:
                p.task_id = None
            return p, "live"
        except llm.LLMError:
            pass
    return parse_offline(question, known_tasks, previous_task), "offline"


def _card_block(c: Card) -> str:
    return (
        f"[{c.card_id} v{c.version}] compito={c.task_id} · vale per: {c.context.value}\n"
        f"Azione: {c.action.value}\nPerché: {c.rationale.value}"
    )


def _template_answer(cards: list[Card]) -> str:
    c = cards[0]
    return f"{c.action.value.rstrip('.')}. Motivo: {c.rationale.value.rstrip('.')}. [{c.card_id} v{c.version}]"


def answer(question: str, store: Store, previous_task: str | None = None) -> AnswerTrace:
    latest = store.all_latest()
    known = sorted({c.task_id for c in latest})
    parsed, parse_mode = parse_question(question, known, previous_task)
    candidates = [c for c in latest if c.task_id == parsed.task_id]
    used, outcome = applicable(latest, parsed.task_id, parsed.context)

    mode = "live" if parse_mode == "live" else "offline"
    if outcome == "answered":
        text = None
        if not llm.offline():
            try:
                text = llm.chat_text(ANSWER_SYSTEM, f"Domanda: {question}\n\nSchede:\n" + "\n\n".join(map(_card_block, used)))
            except llm.LLMError:
                text = None
        if text is None:
            text, mode = _template_answer(used), "offline"
    else:
        text = REFUSAL_TEXT[outcome]
        if outcome == "context_mismatch" and parsed.context is None:
            text = "La domanda non dice a quale variante si riferisce: indicala e controllo se esiste una scheda pubblicata."
        drafts = [c for c in candidates if c.status == "bozza"]
        if drafts:
            text += " Bozze in revisione: " + ", ".join(f"{d.card_id} v{d.version}" for d in drafts) + "."

    trace = AnswerTrace(
        trace_id=uuid.uuid4().hex[:8],
        asked_at=datetime.now(),
        question=question,
        task_id=parsed.task_id,
        context=parsed.context,
        candidate_cards=[(c.card_id, c.version) for c in candidates],
        used_cards=[(c.card_id, c.version) for c in used],
        rule_outcome=outcome,
        answer=text,
        mode=mode,
    )
    store.save_trace(trace)
    return trace
