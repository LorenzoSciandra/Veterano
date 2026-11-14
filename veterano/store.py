"""Persistenza SQLite: schede versionate (append-only), segmenti immutabili, tracce delle risposte.

Ogni modifica a una scheda crea una nuova riga (card_id, version): la storia non si cancella mai.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import AnswerTrace, Card, FieldName, Segment
from .rules import can_publish

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "veterano.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS segments (segment_id TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cards (
    card_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL,
    PRIMARY KEY (card_id, version)
);
CREATE TABLE IF NOT EXISTS traces (trace_id TEXT PRIMARY KEY, asked_at TEXT NOT NULL, body TEXT NOT NULL);
"""


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.executescript(_SCHEMA)

    # --- segmenti -------------------------------------------------------
    def add_segment(self, seg: Segment) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO segments(segment_id, body) VALUES (?, ?)", (seg.segment_id, seg.model_dump_json())
            )

    def segment(self, segment_id: str) -> Segment:
        row = self.db.execute("SELECT body FROM segments WHERE segment_id = ?", (segment_id,)).fetchone()
        if row is None:
            raise KeyError(segment_id)
        return Segment.model_validate_json(row[0])

    def segments(self) -> list[Segment]:
        return [Segment.model_validate_json(r[0]) for r in self.db.execute("SELECT body FROM segments ORDER BY segment_id")]

    def next_segment_id(self, source_id: str) -> str:
        n = self.db.execute("SELECT COUNT(*) FROM segments WHERE segment_id LIKE ?", (source_id + "#%",)).fetchone()[0]
        return f"{source_id}#{n + 1}"

    # --- schede ---------------------------------------------------------
    def save_card(self, card: Card) -> Card:
        card = card.model_copy(update={"missing_fields": card.computed_missing()})
        with self.db:
            self.db.execute(
                "INSERT INTO cards(card_id, version, body) VALUES (?, ?, ?)",
                (card.card_id, card.version, card.model_dump_json()),
            )
        return card

    def latest(self, card_id: str) -> Card:
        row = self.db.execute(
            "SELECT body FROM cards WHERE card_id = ? ORDER BY version DESC LIMIT 1", (card_id,)
        ).fetchone()
        if row is None:
            raise KeyError(card_id)
        return Card.model_validate_json(row[0])

    def all_latest(self, task_id: str | None = None) -> list[Card]:
        rows = self.db.execute(
            """SELECT c.body FROM cards c
               JOIN (SELECT card_id, MAX(version) v FROM cards GROUP BY card_id) m
                 ON c.card_id = m.card_id AND c.version = m.v
               ORDER BY c.card_id"""
        ).fetchall()
        cards = [Card.model_validate_json(r[0]) for r in rows]
        return [c for c in cards if task_id is None or c.task_id == task_id]

    def history(self, card_id: str) -> list[Card]:
        rows = self.db.execute("SELECT body FROM cards WHERE card_id = ? ORDER BY version", (card_id,)).fetchall()
        return [Card.model_validate_json(r[0]) for r in rows]

    def _new_version(self, card: Card, **update) -> Card:
        nxt = card.model_copy(
            update={"version": card.version + 1, "supersedes_version": card.version, **update}, deep=True
        )
        return self.save_card(nxt)

    def publish(self, card_id: str, reviewer: str) -> Card:
        card = self.latest(card_id)
        ok, reason = can_publish(card)
        if not ok:
            raise ValueError(reason)
        return self._new_version(card, status="pubblicata", reviewer=reviewer, reviewed_at=datetime.now())

    def reject(self, card_id: str, reviewer: str) -> Card:
        card = self.latest(card_id)
        return self._new_version(card, status="respinta", reviewer=reviewer, reviewed_at=datetime.now())

    def answer_with_field(self, card_id: str, field: FieldName, segment: Segment, value: str | None = None) -> Card:
        """Risposta dell'esperto a una domanda R1/R2: salva il segmento e crea una nuova versione bozza.

        `value` è il valore normalizzato del campo (es. "P-17 variante A"); se None si usa il testo del segmento.
        """
        self.add_segment(segment)
        card = self.latest(card_id)
        fv = card.field(field).model_copy(deep=True)
        fv.value = value if value is not None else segment.text
        fv.segment_ids = [*fv.segment_ids, segment.segment_id]
        return self._new_version(card, **{field: fv, "status": "bozza", "reviewer": None, "reviewed_at": None})

    # --- tracce ---------------------------------------------------------
    def save_trace(self, t: AnswerTrace) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO traces(trace_id, asked_at, body) VALUES (?, ?, ?)",
                (t.trace_id, t.asked_at.isoformat(), t.model_dump_json()),
            )

    def traces(self, limit: int = 50) -> list[AnswerTrace]:
        rows = self.db.execute("SELECT body FROM traces ORDER BY asked_at DESC LIMIT ?", (limit,)).fetchall()
        return [AnswerTrace.model_validate_json(r[0]) for r in rows]

    # --- fixture --------------------------------------------------------
    def load_fixtures(self, path: Path | str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for s in data["segments"]:
            self.add_segment(Segment.model_validate(s))
        for c in data["cards"]:
            self.save_card(Card.model_validate(c))

    def reset(self) -> None:
        with self.db:
            self.db.executescript("DELETE FROM segments; DELETE FROM cards; DELETE FROM traces;")
