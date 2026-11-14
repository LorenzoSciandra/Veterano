"""Registra il percorso demo vero con un browser automatico (Playwright) -> delivery/out/demo.webm.

Prerequisiti (fuori da requirements.txt): pip install playwright && python -m playwright install chromium
Avvio: un'istanza dedicata dell'app su un DB separato, per non toccare quella di prova:
  VETERANO_DB=data/record.db .venv/bin/streamlit run app.py --server.port 8502 --server.headless true
  <venv con playwright>/bin/python delivery/record_demo.py http://localhost:8502
"""
from __future__ import annotations

import sys
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8502"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
SIZE = {"width": 1280, "height": 720}
EVENTS: list[tuple[str, float]] = []
T0 = [0.0]


def mark(name):
    EVENTS.append((name, round(time.monotonic() - T0[0], 2)))


def pause(page, ms=1200):
    page.wait_for_timeout(ms)


def wait_idle(page):
    # Streamlit mostra "Running..." mentre esegue: aspetta che sparisca
    page.wait_for_timeout(400)
    page.wait_for_function("() => !document.querySelector('[data-testid=\"stStatusWidget\"]')", timeout=60000)
    page.wait_for_timeout(300)


def click(page, name, exact=False):
    page.get_by_role("button", name=name, exact=exact).first.click()
    wait_idle(page)


def ask(page, text, hold=2200):
    box = page.get_by_label("Domanda dell'operatore")
    box.fill(text)
    pause(page, 500)
    click(page, "Chiedi")
    mark("answer:" + text)
    pause(page, hold)


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport=SIZE, record_video_dir=str(OUT), record_video_size=SIZE)
    page = ctx.new_page()
    T0[0] = time.monotonic()
    page.goto(URL)
    page.get_by_text("Il Veterano").first.wait_for(timeout=60000)
    wait_idle(page)
    click(page, "↺ Ripristina demo")
    mark("reset")
    pause(page, 600)

    # 1. domanda -> rifiuto: solo bozza
    mark("ask1")
    ask(page, "Come controllo la P-17 variante A?", hold=3500)
    # 2. apro la bozza
    click(page, "CARD-P17-VIS-01 v1")
    mark("draft_open")
    pause(page, 3000)
    # 3-4. l'esperto risponde alle domande R1 e R2
    for answer in (
        "Alla variante A; per la B usiamo un'altra scheda.",
        "Così non registro come buono un pezzo con un difetto che a occhio non si vede.",
    ):
        page.get_by_label("Risposta dell'esperto (parole esatte)").first.fill(answer)
        pause(page, 600)
        click(page, "Collega la risposta alla scheda")
        mark("linked")
        pause(page, 1800)
    # 5. il responsabile pubblica
    page.mouse.wheel(0, 400)
    pause(page, 800)
    click(page, "✅ Pubblica")
    mark("published")
    pause(page, 2500)
    # 6. stessa domanda -> risposta con v4; poi variante B -> nessuna scheda
    page.get_by_text("Assistente", exact=True).first.click()
    wait_idle(page)
    mark("ask2")
    ask(page, "Come controllo la P-17 variante A?", hold=4500)
    mark("ask3")
    ask(page, "E per la variante B?", hold=3500)
    mark("end")

    video = page.video.path()
    ctx.close()
    browser.close()
    (OUT / "events.json").write_text(json.dumps(EVENTS, indent=1))
    print(video)
    print(EVENTS)
