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
SIZE = {"width": 1024, "height": 576}  # finestra piccola: l'app riempie il riquadro e si legge
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


CURSOR_JS = """
(() => {
  const add = () => {
    if (document.getElementById('__cur')) return;
    const c = document.createElement('div'); c.id = '__cur';
    c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;'
      + 'background:rgba(68,167,214,.35);border:3px solid #44A7D6;box-shadow:0 0 18px rgba(68,167,214,.8);'
      + 'z-index:2147483647;pointer-events:none;transition:transform .12s ease;';
    document.body.appendChild(c);
    const tag = document.createElement('div'); tag.id = '__tag';
    tag.style.cssText = 'position:fixed;left:0;top:0;transform:translate(16px,14px);padding:5px 12px;border-radius:7px;'
      + 'font:700 15px/1.1 "Inter Tight",system-ui,sans-serif;letter-spacing:.05em;text-transform:uppercase;'
      + 'color:#0B0A0A;background:#44A7D6;z-index:2147483647;pointer-events:none;box-shadow:0 4px 14px rgba(0,0,0,.5);';
    tag.textContent = 'Operatore';
    document.body.appendChild(tag);
    window.__setRole = (name, color) => {
      tag.textContent = name; tag.style.background = color;
      c.style.borderColor = color; c.style.boxShadow = `0 0 18px ${color}`; c.style.background = color + '55';
      tag.animate([{ transform: 'translate(16px,14px) scale(1.35)' }, { transform: 'translate(16px,14px) scale(1)' }], { duration: 380, easing: 'ease-out' });
    };
    document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
      tag.style.left = e.clientX + 'px'; tag.style.top = e.clientY + 'px'; }, true);
    document.addEventListener('mousedown', e => {
      c.style.transform = 'scale(.7)';
      const r = document.createElement('div');
      r.style.cssText = `position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:16px;height:16px;margin:-8px 0 0 -8px;`
        + 'border-radius:50%;border:3px solid #44A7D6;z-index:2147483646;pointer-events:none;'
        + 'transition:all .6s ease-out;opacity:1;';
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.width = '70px'; r.style.height = '70px'; r.style.margin = '-35px 0 0 -35px'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 700);
    }, true);
    document.addEventListener('mouseup', () => { c.style.transform = 'scale(1)'; }, true);
  };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
})();
"""


ROLES = {"Operatore": "#44A7D6", "Esperto": "#E8A33D", "Capo reparto": "#3FB97F"}


def role(page, name):
    page.evaluate("([n, c]) => window.__setRole(n, c)", [name, ROLES[name]])
    page.wait_for_timeout(500)


def human_click(page, locator):
    locator.scroll_into_view_if_needed()
    page.wait_for_timeout(150)
    b = locator.bounding_box()
    x, y = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    page.mouse.move(x, y, steps=22)
    page.wait_for_timeout(220)
    page.mouse.down()
    page.wait_for_timeout(90)
    page.mouse.up()


def click(page, name):
    human_click(page, page.get_by_role("button", name=name).first)
    wait_idle(page)


def nav(page, name):
    human_click(page, page.locator('div[role="radiogroup"] label').filter(has_text=name).first)
    wait_idle(page)


def type_slow(locator, text, page=None):
    if page is not None:
        human_click(page, locator)
    else:
        locator.click()
    locator.press_sequentially(text, delay=32)


def ask(page, text, hold):
    type_slow(page.get_by_label("La tua domanda"), text, page)
    page.wait_for_timeout(300)
    human_click(page, page.get_by_role("button", name="Chiedi").first)
    # aspetta che compaia la risposta vera (la domanda entra in chat, in alto, solo a risposta pronta)
    page.wait_for_function(
        "q => { const b = document.querySelector('.bubble.me'); return b && b.innerText.includes(q); }", arg=text, timeout=60000
    )
    wait_idle(page)
    page.locator(".bubble.bot").first.scroll_into_view_if_needed()
    page.mouse.wheel(0, 140)
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
    page.add_init_script(CURSOR_JS)
    T0[0] = time.monotonic()
    page.goto(URL)
    page.get_by_text("Il Veterano").first.wait_for(timeout=60000)
    wait_idle(page)
    page.mouse.move(700, 420)
    role(page, "Operatore")

    mark("ask1")
    ask(page, "Come controllo la P-17 variante A?", hold=2600)          # rifiuto: non approvata
    if page.get_by_role("button", name="Completa l'istruzione").count() == 0:
        page.screenshot(path=str(OUT / "fail.png"))
        print("BOT:", page.locator(".bubble.bot").all_inner_texts())
    role(page, "Esperto")
    click(page, "Completa l'istruzione")
    mark("card_open")
    page.wait_for_timeout(2400)                                          # "Vale per: manca", "Perché: manca"
    for answer in (
        "Alla variante A. Per la B usiamo un'altra scheda.",
        "Così non segno come buono un pezzo con un difetto che a occhio non si vede.",
    ):
        page.locator(".ask").first.scroll_into_view_if_needed()
        page.wait_for_timeout(900)
        type_slow(page.get_by_label("Risposta dell'esperto"), answer, page)
        page.wait_for_timeout(300)
        before = page.locator(".ask").first.inner_text()
        human_click(page, page.get_by_role("button", name="Salva risposta").first)
        # aspetta che la domanda cambi (o sparisca): la risposta è stata salvata
        page.wait_for_function(
            "b => { const a = document.querySelector('.ask'); return !a || a.innerText !== b; }", arg=before, timeout=60000
        )
        wait_idle(page)
        mark("saved")
        page.wait_for_timeout(1200)
    role(page, "Capo reparto")
    page.mouse.wheel(0, -2000)   # torna su: si vedono i campi ora completi
    page.wait_for_timeout(1500)
    click(page, "✓ Approva e pubblica")
    mark("published")
    page.wait_for_timeout(2200)
    role(page, "Operatore")
    nav(page, "Chiedi")
    mark("ask2")
    ask(page, "Come controllo la P-17 variante A?", hold=3400)          # risposta approvata, con fonte
    mark("ask3")
    ask(page, "E per la variante B?", hold=3200)                          # nessuna istruzione per B
    mark("end")

    video = page.video.path()
    ctx.close()
    browser.close()
    (OUT / "events.json").write_text(json.dumps(EVENTS, indent=1))
    print(video)
    print(EVENTS)
