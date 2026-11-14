"""Registra il percorso demo vero con un browser automatico (Playwright) -> delivery/out/demo.webm + events.json.

Prerequisiti (fuori da requirements.txt): pip install playwright && python -m playwright install chromium
Avvio: un'istanza dedicata dell'app su un DB separato, per non toccare quella di prova:
  VETERANO_DB=data/record.db .venv/bin/streamlit run app.py --server.port 8502 --server.headless true
  <venv con playwright>/bin/python delivery/record_demo.py http://localhost:8502
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

import subprocess

ROOT = Path(__file__).resolve().parent.parent

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8502"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
SIZE = {"width": 1280, "height": 720}
EVENTS: list[tuple[str, float]] = []
T0 = [0.0]


def mark(name):
    EVENTS.append((name, round(time.monotonic() - T0[0], 2)))


def wait_idle(page):
    page.wait_for_timeout(400)
    # con la toolbar nascosta lo status widget non c'è: aspetta anche che sparisca lo spinner
    page.wait_for_function(
        "() => !document.querySelector('[data-testid=\"stStatusWidget\"]') && !document.querySelector('[data-testid=\"stSpinner\"]')",
        timeout=60000,
    )
    page.wait_for_timeout(300)


def click(page, name):
    page.get_by_role("button", name=name).first.click()
    wait_idle(page)


def nav(page, name):
    page.locator('div[role="radiogroup"] label').filter(has_text=name).first.click()
    wait_idle(page)


def type_slow(locator, text):
    locator.click()
    locator.press_sequentially(text, delay=28)


def ask(page, text, hold):
    type_slow(page.get_by_label("La tua domanda"), text)
    page.wait_for_timeout(300)
    n = page.locator(".bubble.me").count()
    page.get_by_role("button", name="Chiedi").first.click()
    # aspetta che compaia la risposta vera (la domanda entra in chat solo a risposta pronta)
    page.wait_for_function(f"document.querySelectorAll('.bubble.me').length > {n}", timeout=60000)
    wait_idle(page)
    mark("answer:" + text)
    page.wait_for_timeout(hold)


# scenario pulito prima di registrare (non si vede nel video)
subprocess.run([str(ROOT / ".venv" / "bin" / "python"), "-c",
    "from veterano.store import Store; s=Store('data/record.db'); s.reset(); s.load_fixtures('data/fixtures/p17.json')"],
    cwd=ROOT, check=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport=SIZE, record_video_dir=str(OUT), record_video_size=SIZE)
    page = ctx.new_page()
    T0[0] = time.monotonic()
    page.goto(URL)
    page.get_by_text("Il Veterano").first.wait_for(timeout=60000)
    wait_idle(page)
    page.wait_for_timeout(500)

    mark("ask1")
    ask(page, "Come controllo la P-17 variante A?", hold=3200)          # rifiuto: non approvata
    click(page, "Completa l'istruzione")
    mark("card_open")
    page.wait_for_timeout(2600)                                          # "Vale per: manca", "Perché: manca"
    for answer in (
        "Alla variante A. Per la B usiamo un'altra scheda.",
        "Così non segno come buono un pezzo con un difetto che a occhio non si vede.",
    ):
        type_slow(page.get_by_label("Risposta dell'esperto"), answer)
        page.wait_for_timeout(300)
        before = page.locator(".ask").first.inner_text()
        page.get_by_role("button", name="Salva risposta").first.click()
        # aspetta che la domanda cambi (o sparisca): la risposta è stata salvata
        page.wait_for_function(
            "b => { const a = document.querySelector('.ask'); return !a || a.innerText !== b; }", arg=before, timeout=60000
        )
        wait_idle(page)
        mark("saved")
        page.wait_for_timeout(1800)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(700)
    click(page, "✓ Approva e pubblica")
    mark("published")
    page.wait_for_timeout(2200)
    nav(page, "Chiedi")
    mark("ask2")
    ask(page, "Come controllo la P-17 variante A?", hold=3800)          # risposta approvata, con fonte
    mark("ask3")
    ask(page, "E per la variante B?", hold=3200)                          # nessuna istruzione per B
    mark("end")

    video = page.video.path()
    ctx.close()
    browser.close()
    (OUT / "events.json").write_text(json.dumps(EVENTS, indent=1))
    print(video)
    print(EVENTS)
