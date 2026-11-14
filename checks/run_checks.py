"""Esegue il check set e stampa passed/total. Deterministico: non chiama il modello.

Uso: .venv/bin/python -m checks.run_checks
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from veterano.models import Card, FieldValue, Segment  # noqa: E402
from veterano.rules import applicable, can_publish, detect_gaps  # noqa: E402
from veterano.store import Store  # noqa: E402

FIXTURES = ROOT / "data" / "fixtures" / "p17.json"
CASES = ROOT / "checks" / "cases.json"


def fresh_store() -> Store:
    s = Store(":memory:")
    s.load_fixtures(FIXTURES)
    return s


def _seg(store: Store, text: str) -> Segment:
    src = "SRC-LIVE"
    return Segment(
        segment_id=store.next_segment_id(src),
        source_id=src,
        expert="Esperto 1 (simulato)",
        text=text,
        recorded_at=datetime.now(),
    )


def run_case(case: dict) -> tuple[bool, str]:
    s = fresh_store()
    exp = case["expect"]
    op = case["op"]

    if op == "ask":
        used, outcome = applicable(s.all_latest(), case["task_id"], case["context"])
        got = {"outcome": outcome, "used": [c.card_id for c in used]}
        return got == {"outcome": exp["outcome"], "used": exp["used"]}, str(got)

    if op == "gaps":
        rules = [g.rule for g in detect_gaps(s.latest(case["card_id"]))]
        return rules == exp["rules"], str(rules)

    if op == "fill_then_publish":
        for field, text in case["fill"].items():
            s.answer_with_field(case["card_id"], field, _seg(s, text))
        ok, reason = can_publish(s.latest(case["card_id"]))
        passed = ok == exp["can_publish"] and exp["reason_contains"] in reason
        return passed, f"can_publish={ok} reason={reason!r}"

    if op == "demo_flow_then_ask":
        cid = case["card_id"]
        for field in ("context", "rationale"):
            text = case["answers"][field]
            s.answer_with_field(cid, field, _seg(s, text), value=text)
        s.publish(cid, reviewer="Capo reparto (simulato)")
        ask = case["ask"]
        used, outcome = applicable(s.all_latest(), ask["task_id"], ask["context"])
        got = {"outcome": outcome, "used": [c.card_id for c in used]}
        passed = got == {"outcome": exp["outcome"], "used": exp["used"]}
        if passed and "used_version" in exp:
            passed = used[0].version == exp["used_version"]
            got["version"] = used[0].version
        return passed, str(got)

    if op == "save_and_detect_conflict":
        nc = case["new_card"]
        card = Card(
            card_id=nc["card_id"], version=1, status="bozza", task_id=nc["task_id"],
            context=FieldValue(value=nc["context"]), action=FieldValue(value=nc["action"]),
            rationale=FieldValue(), expert="Esperto 2 (simulato)",
        )
        saved = s.save_card(card)
        return saved.conflicts == exp["conflicts"], f"conflicts={saved.conflicts}"

    return False, f"op sconosciuta: {op}"


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    passed = total = 0
    skipped = []
    for case in cases:
        if case.get("not_implemented"):
            skipped.append(case)
            continue
        total += 1
        try:
            ok, detail = run_case(case)
        except Exception as e:  # un'eccezione è un fallimento, non un crash del runner
            ok, detail = False, f"{type(e).__name__}: {e}"
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['id']}  [{case['group']}]  {detail}")
    for case in skipped:
        print(f"SKIP  {case['id']}  [{case['group']}]  not_implemented: {case['not_implemented']}")
    print(f"\n{passed}/{total} passed · {len(skipped)} not implemented (su {len(cases)} casi)")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
