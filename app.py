"""Il Veterano — UI. Due schermate: «Chiedi» (operatore) e «Schede» (esperto e responsabile).

Principi (studio di usabilità, 14/11): una sola prossima azione per schermata; chiaro chi scrive cosa
(operatore a destra, Il Veterano a sinistra); linguaggio da officina, nessun codice tecnico in primo piano;
testo grande e contrasto alto per proiettore e utenti poco digitali.
Avvio: .venv/bin/streamlit run app.py
"""
from __future__ import annotations

import html
import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

from veterano import assistant, extract, llm
from veterano.models import AnswerTrace, Card, Segment
from veterano.rules import can_publish, detect_gaps
from veterano.store import DEFAULT_DB, Store

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "data" / "fixtures" / "p17.json"
LABEL = {"context": "Vale per", "action": "Cosa fare", "rationale": "Perché"}
STATUS = {"bozza": ("Da completare", "amber"), "pubblicata": ("Approvata", "green"), "respinta": ("Respinta", "red")}

st.set_page_config(page_title="Il Veterano", page_icon="🛠️", layout="centered", initial_sidebar_state="collapsed")
st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root { --ink:#0B0A0A; --card:#161515; --line:rgba(255,255,255,.14); --dim:rgba(255,255,255,.62);
        --blue:#44A7D6; --green:#3FB97F; --amber:#E8A33D; --red:#D0425A; }
html, body, .stApp, [class*="css"], input, textarea, button { font-family:"Inter Tight", system-ui, sans-serif !important; }
.stApp { background: var(--ink); }
[data-testid="stSidebar"], [data-testid="collapsedControl"], header [data-testid="stToolbar"] { display:none; }
.block-container { max-width: 980px; padding-top: 1rem; }
p, li, label, .stMarkdown { font-size: 21px !important; }
h1 { font-weight: 400 !important; letter-spacing: -0.02em; text-transform: uppercase; font-size: 46px !important; }
h1 .b { color: var(--blue); }
.sub { color: var(--dim); font-size: 19px; margin: -10px 0 18px; }
.bubble { border-radius: 16px; padding: 16px 20px; margin: 10px 0; font-size: 22px; line-height: 1.4; max-width: 85%; }
.me { background: #1F3A4A; margin-left: auto; border-bottom-right-radius: 4px; }
.me .who, .bot .who { font-size: 14px; color: var(--dim); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.bot { background: var(--card); border: 1px solid var(--line); border-left: 6px solid var(--blue); border-bottom-left-radius: 4px; }
.bot.green { border-left-color: var(--green); } .bot.amber { border-left-color: var(--amber); } .bot.red { border-left-color: var(--red); }
.head { font-weight: 700; font-size: 18px; text-transform: uppercase; letter-spacing: .03em; margin-bottom: 6px; }
.green .head { color: var(--green); } .amber .head { color: var(--amber); }
.src { font-size: 16px; color: var(--dim); margin-top: 10px; }
.row { display:flex; gap:18px; padding: 14px 0; border-bottom: 1px solid var(--line); }
.row .k { width: 150px; flex: none; color: var(--dim); font-size: 18px; text-transform: uppercase; padding-top: 3px; }
.row .v { font-size: 22px; }
.row .v.miss { color: var(--amber); font-weight: 700; }
.quote { color: var(--dim); font-style: italic; font-size: 18px; margin-top: 4px; }
.chip { display:inline-block; padding: 3px 12px; border-radius: 999px; font-size: 15px; font-weight: 700; text-transform: uppercase; }
.chip.green { background: rgba(63,185,127,.18); color: var(--green); }
.chip.amber { background: rgba(232,163,61,.18); color: var(--amber); }
.chip.red { background: rgba(208,66,90,.18); color: var(--red); }
.ask { background: #10222C; border: 1px solid var(--blue); border-radius: 14px; padding: 16px 20px; font-size: 22px; margin: 8px 0 4px; }
.ask .who { font-size: 14px; color: var(--blue); text-transform: uppercase; letter-spacing: .04em; }
.done { background: rgba(63,185,127,.12); border: 1px solid var(--green); border-radius: 14px; padding: 16px 20px; font-size: 21px; }
.stButton button, .stFormSubmitButton button { font-size: 20px !important; padding: .55rem 1.3rem !important; border-radius: 10px !important; }
.stTextInput input { font-size: 21px !important; padding: .7rem .9rem !important; }
div[role="radiogroup"] label p { font-size: 22px !important; }
.mode { text-align:right; color: var(--dim); font-size: 14px; text-transform: uppercase; letter-spacing: .04em; }
</style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_store() -> Store:
    s = Store(os.getenv("VETERANO_DB", DEFAULT_DB))
    if not s.all_latest():
        s.load_fixtures(FIXTURES)
    return s


store = get_store()
ss = st.session_state
ss.setdefault("page", "Chiedi")
ss.setdefault("selected", None)
ss.setdefault("chat", [])  # list[AnswerTrace]


def e(text: str | None) -> str:
    return html.escape(text or "")


def task_title(task_id: str) -> str:
    """'P17-controllo-visivo' -> 'Controllo visivo · P-17'."""
    m = re.match(r"P(\d+)-(.+)", task_id)
    if m:
        return f"{m.group(2).replace('-', ' ').capitalize()} · P-{m.group(1)}"
    return task_id.replace("-", " ").capitalize()


def go_card(card_id: str) -> None:
    ss.page, ss.selected = "Schede", card_id


def go_list() -> None:
    ss.selected = None


# --- intestazione -----------------------------------------------------------
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown("<h1><span class='b'>Il Veterano</span></h1>", unsafe_allow_html=True)
with top_r:
    st.markdown(f"<div class='mode'>{'● live' if llm.mode() == 'live' else '○ offline'}<br>scenario simulato</div>", unsafe_allow_html=True)
st.radio("Schermata", ["Chiedi", "Schede"], key="page", horizontal=True, label_visibility="collapsed")


# --- CHIEDI -------------------------------------------------------------------
def render_answer(t: AnswerTrace) -> None:
    st.markdown(f"<div class='bubble me'><div class='who'>Operatore</div>{e(t.question)}</div>", unsafe_allow_html=True)
    if t.rule_outcome == "answered":
        cid, ver = t.used_cards[0]
        c = next(h for h in store.history(cid) if h.version == ver)
        text = re.sub(r"\s*\[CARD-[^\]]+\]\s*$", "", t.answer)
        src = f"Fonte: {e(task_title(c.task_id))} · {e(c.context.value)} · versione {ver} · approvata da {e(c.reviewer)}"
        st.markdown(
            f"<div class='bubble bot green'><div class='head'>✓ Istruzione approvata</div>{e(text)}<div class='src'>{src}</div></div>",
            unsafe_allow_html=True,
        )
        st.button("Vedi la scheda", key=f"see-{t.trace_id}", on_click=go_card, args=(cid,))
        return
    drafts = [cid for cid, _ in t.candidate_cards if store.latest(cid).status == "bozza"]
    if t.rule_outcome == "no_published_card":
        head, body = "Non rispondo ancora", "C'è un'istruzione dell'esperto, ma nessun responsabile l'ha ancora approvata."
    elif t.rule_outcome == "context_mismatch" and t.context:
        head, body = "Non rispondo", f"Non ho istruzioni approvate per {e(t.context)}. Chiedi al responsabile."
    elif t.rule_outcome == "context_mismatch":
        head, body = "Mi serve un dettaglio", "Per quale variante o condizione? Indicala e controllo."
    else:
        head, body = "Non rispondo", "Non ho istruzioni su questo argomento. Non invento."
    st.markdown(f"<div class='bubble bot amber'><div class='head'>⏸ {head}</div>{body}</div>", unsafe_allow_html=True)
    if drafts:
        st.button("Completa l'istruzione", key=f"fix-{t.trace_id}", on_click=go_card, args=(drafts[0],), type="primary")


def page_ask() -> None:
    st.markdown("<div class='sub'>Fai una domanda come la faresti al collega esperto.</div>", unsafe_allow_html=True)
    with st.form("ask", clear_on_submit=True):
        q = st.text_input("La tua domanda", placeholder="Es. Come controllo la P-17 variante A?", label_visibility="collapsed")
        sent = st.form_submit_button("Chiedi", type="primary")
    if sent and q.strip():
        prev = ss.chat[-1].task_id if ss.chat else None
        with st.spinner("Cerco tra le istruzioni approvate…"):
            ss.chat.append(assistant.answer(q.strip(), store, previous_task=prev))
    for t in reversed(ss.chat[-2:]):  # meno ma meglio: l'ultimo scambio in alto, al massimo due
        render_answer(t)


# --- SCHEDE -------------------------------------------------------------------
def page_cards() -> None:
    if ss.selected:
        card_view(store.latest(ss.selected))
        return
    st.markdown("<div class='sub'>Le istruzioni del reparto. Prima quelle da completare.</div>", unsafe_allow_html=True)
    cards = sorted(store.all_latest(), key=lambda c: (c.status != "bozza", c.task_id))
    for c in cards:
        label, color = STATUS[c.status]
        cols = st.columns([5, 2])
        cols[0].markdown(
            f"<div style='font-size:23px'>{e(task_title(c.task_id))}</div>"
            f"<div class='quote' style='font-style:normal'>{e(c.context.value or 'variante da chiarire')}</div>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(f"<span class='chip {color}'>{label}</span>", unsafe_allow_html=True)
        cols[1].button("Apri", key=f"open-{c.card_id}", on_click=go_card, args=(c.card_id,))
        st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,.1)'></div>", unsafe_allow_html=True)
    new_story_box()
    with st.expander("Strumenti demo"):
        if st.button("Ripristina scenario demo"):
            store.reset()
            store.load_fixtures(FIXTURES)
            ss.selected, ss.chat = None, []
            st.rerun()


def card_view(c: Card) -> None:
    st.button("← Tutte le schede", on_click=go_list)
    label, color = STATUS[c.status]
    st.markdown(
        f"<div style='font-size:30px;margin:6px 0'>{e(task_title(c.task_id))} &nbsp;<span class='chip {color}'>{label}</span></div>",
        unsafe_allow_html=True,
    )
    rows = []
    for name in ("context", "action", "rationale"):
        fv = c.field(name)  # type: ignore[arg-type]
        quotes = "".join(f"<div class='quote'>“{e(store.segment(s).text)}” — {e(store.segment(s).expert)}</div>" for s in fv.segment_ids)
        val = f"<div class='v'>{e(fv.value)}</div>{quotes}" if not fv.missing else "<div class='v miss'>manca</div>"
        rows.append(f"<div class='row'><div class='k'>{LABEL[name]}</div><div>{val}</div></div>")
    st.markdown("".join(rows), unsafe_allow_html=True)

    if c.status == "pubblicata":
        st.markdown(
            f"<div class='done' style='margin-top:18px'>✓ Approvata da {e(c.reviewer)} · versione {c.version}. L'assistente la usa per rispondere.</div>",
            unsafe_allow_html=True,
        )
    elif c.status == "bozza":
        gaps = detect_gaps(c)
        if gaps:
            g = gaps[0]  # una domanda alla volta
            left = f" · ne resta {len(gaps) - 1}" if len(gaps) > 1 else ""
            st.markdown(
                f"<div class='ask' style='margin-top:18px'><div class='who'>Il Veterano chiede all'esperto{left}</div>{e(g.question)}</div>",
                unsafe_allow_html=True,
            )
            with st.form(f"gap-{c.card_id}-{c.version}", clear_on_submit=True):
                ans = st.text_input("Risposta dell'esperto", placeholder="Scrivi o detta la risposta, con parole sue")
                if st.form_submit_button("Salva risposta", type="primary") and ans.strip():
                    val, _ = extract.propose_value(g.field, ans, c)
                    seg = Segment(segment_id=store.next_segment_id("SRC-LIVE"), source_id="SRC-LIVE",
                                  expert=c.expert, text=ans.strip(), recorded_at=datetime.now())
                    store.answer_with_field(c.card_id, g.field, seg, value=val)
                    st.rerun()
        else:
            ok, reason = can_publish(c)
            if ok:
                st.markdown("<div class='done' style='margin-top:18px'>Completa. Controlla le parole dell'esperto qui sopra e approva.</div>", unsafe_allow_html=True)
                rev = st.text_input("Approvata da", value="Capo reparto")
                if st.button("✓ Approva e pubblica", type="primary"):
                    store.publish(c.card_id, rev)
                    st.rerun()
            else:
                st.warning(reason.replace("Conflitto aperto con", "In contrasto con un'altra istruzione approvata"))
    with st.expander("Storico modifiche"):
        for h in store.history(c.card_id):
            who = f" · {h.reviewer}" if h.reviewer else ""
            st.markdown(f"versione {h.version} · {STATUS[h.status][0].lower()}{who} · `{h.card_id}`")


def new_story_box() -> None:
    with st.expander("➕ Nuovo racconto di un esperto"):
        with st.form("story", clear_on_submit=True):
            expert = st.text_input("Chi racconta", value="Esperto (simulato)")
            story = st.text_area("Il racconto, con parole sue", height=120)
            if st.form_submit_button("Crea la scheda", type="primary") and story.strip():
                known = sorted({x.task_id for x in store.all_latest()})
                with st.spinner("Leggo il racconto…"):
                    card, segs, _ = extract.extract_card(
                        story, expert, f"SRC-{datetime.now():%H%M%S}", f"CARD-NEW-{len(store.all_latest()) + 1:02d}", known
                    )
                for s in segs:
                    store.add_segment(s)
                store.save_card(card)
                go_card(card.card_id)
                st.rerun()


if ss.page == "Chiedi":
    page_ask()
else:
    page_cards()
