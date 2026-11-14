"""Regole deterministiche R1, R2, R3. Nessuna chiamata al modello in questo file.

R1 contesto mancante  -> domanda mirata sulla variante/condizione.
R2 motivazione mancante -> domanda mirata su quale errore evita.
R3 applicabilità: solo schede pubblicate, con fonte sull'azione e contesto compatibile.
"""
from __future__ import annotations

import re
import unicodedata

from .models import Card, GapQuestion, RuleOutcome

R1_TEMPLATE = "A quale variante o condizione si applica: «{action}»?"
R2_TEMPLATE = "Quale errore evita, o quale esito permette di riconoscere: «{action}»?"


def normalize(text: str | None) -> str:
    """Normalizza un contesto per il confronto: minuscole, senza accenti, punteggiatura e spazi ridotti.

    "P-17 variante A" == "p17 variante a" == "P 17 – Variante A".
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    # "p 17" -> "p17": codici pezzo scritti con o senza trattino
    t = re.sub(r"\b([a-z])\s+(\d+)\b", r"\1\2", t)
    return " ".join(t.split())


def detect_gaps(card: Card) -> list[GapQuestion]:
    action = card.action.value or "questo accorgimento"
    gaps: list[GapQuestion] = []
    if card.context.missing:
        gaps.append(
            GapQuestion(card_id=card.card_id, field="context", rule="R1", question=R1_TEMPLATE.format(action=action))
        )
    if card.rationale.missing:
        gaps.append(
            GapQuestion(card_id=card.card_id, field="rationale", rule="R2", question=R2_TEMPLATE.format(action=action))
        )
    return gaps


def can_publish(card: Card) -> tuple[bool, str]:
    missing = card.computed_missing()
    if missing:
        return False, "Campi mancanti: " + ", ".join(missing)
    for name in ("context", "action", "rationale"):
        fv = card.field(name)  # type: ignore[arg-type]
        if not fv.segment_ids:
            return False, f"Il campo «{name}» non ha un frammento di fonte"
    if card.conflicts:
        return False, "Conflitto aperto con: " + ", ".join(card.conflicts)
    if card.status == "pubblicata":
        return False, "Già pubblicata"
    return True, "ok"


def applicable(cards: list[Card], task_id: str | None, context: str | None) -> tuple[list[Card], RuleOutcome]:
    """R3. `cards` = ultima versione di ogni scheda. Restituisce le schede utilizzabili e l'esito.

    Ordine dei motivi di rifiuto: unknown_task -> no_published_card -> missing_source -> context_mismatch.
    """
    on_task = [c for c in cards if task_id and c.task_id == task_id]
    if not on_task:
        return [], "unknown_task"
    published = [c for c in on_task if c.status == "pubblicata"]
    if not published:
        return [], "no_published_card"
    sourced = [c for c in published if c.action.segment_ids]
    if not sourced:
        return [], "missing_source"
    wanted = normalize(context)
    matching = [c for c in sourced if wanted and normalize(c.context.value) == wanted]
    if not matching:
        return [], "context_mismatch"
    return matching, "answered"


REFUSAL_TEXT: dict[str, str] = {
    "unknown_task": "Non ho schede su questo compito: non rispondo per non inventare.",
    "no_published_card": "Esiste solo una bozza non ancora revisionata per questo compito: non la uso finché un responsabile non la pubblica.",
    "missing_source": "Le schede pubblicate per questo compito non hanno un frammento di fonte sull'azione: non le uso.",
    "context_mismatch": "Ho schede pubblicate per questo compito, ma nessuna vale per la variante richiesta.",
}
