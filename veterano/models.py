"""Modelli dati del Veterano. Fonte: CONTRACT.md. Non cambiare nomi o campi senza aggiornare il contratto."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FieldName = Literal["context", "action", "rationale"]
Status = Literal["bozza", "pubblicata", "respinta", "ritirata"]
RuleOutcome = Literal[
    "answered",
    "no_published_card",
    "context_mismatch",
    "missing_source",
    "unknown_task",
]


class Segment(BaseModel):
    """Frammento esatto di una fonte. Il testo non cambia mai."""

    segment_id: str  # "SRC-001#2"
    source_id: str  # "SRC-001"
    expert: str
    text: str
    recorded_at: datetime


class FieldValue(BaseModel):
    """Valore di un campo della scheda. None = mancante, mai inventato."""

    value: str | None = None
    segment_ids: list[str] = Field(default_factory=list)

    @property
    def missing(self) -> bool:
        return self.value is None or not self.value.strip()


class Card(BaseModel):
    card_id: str
    version: int
    status: Status
    task_id: str
    context: FieldValue
    action: FieldValue
    rationale: FieldValue
    expert: str
    missing_fields: list[FieldName] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    reviewer: str | None = None
    reviewed_at: datetime | None = None
    supersedes_version: int | None = None

    def field(self, name: FieldName) -> FieldValue:
        return getattr(self, name)

    def computed_missing(self) -> list[FieldName]:
        """Campi mancanti calcolati dai valori, nell'ordine fisso context, action, rationale."""
        return [f for f in ("context", "action", "rationale") if self.field(f).missing]  # type: ignore[arg-type]


class GapQuestion(BaseModel):
    card_id: str
    field: Literal["context", "rationale"]
    rule: Literal["R1", "R2"]
    question: str


class AnswerTrace(BaseModel):
    trace_id: str
    asked_at: datetime
    question: str
    task_id: str | None
    context: str | None
    candidate_cards: list[tuple[str, int]] = Field(default_factory=list)
    used_cards: list[tuple[str, int]] = Field(default_factory=list)
    rule_outcome: RuleOutcome
    answer: str
    mode: Literal["live", "offline"]
