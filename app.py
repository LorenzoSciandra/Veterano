"""Il Veterano — UI Streamlit: Assistente e Memoria del reparto. Avvio: .venv/bin/streamlit run app.py"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from veterano import assistant, extract, llm
from veterano.models import Card, Segment
from veterano.rules import can_publish, detect_gaps
from veterano.store import DEFAULT_DB, Store

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "data" / "fixtures" / "p17.json"
FIELD_LABEL = {"context": "Vale per (variante/condizione)", "action": "Azione", "rationale": "Perché"}
STATUS_BADGE = {"bozza": "🟡 bozza", "pubblicata": "🟢 pubblicata", "respinta": "🔴 respinta"}
OUTCOME_LABEL = {
    "answered": "🟢 risposta da scheda pubblicata",
    "no_published_card": "🟡 solo bozze: nessuna scheda pubblicata",
    "context_mismatch": "🟠 nessuna scheda per questa variante",
    "missing_source": "🟠 scheda senza fonte",
    "unknown_task": "⚪ compito sconosciuto",
}

st.set_page_config(page_title="Il Veterano", page_icon="🛠️", layout="wide")
st.markdown(
    """<style>
    html, body, [class*="css"] { font-size: 19px; }
    .field-missing { background:#FEE2E2; border-left:6px solid #DC2626; padding:.5rem .8rem; border-radius:6px; }
    .field-ok { background:#F0FDF4; border-left:6px solid #16A34A; padding:.5rem .8rem; border-radius:6px; }
    .quote { color:#475569; font-style:italic; border-left:3px solid #CBD5E1; padding-left:.6rem; margin:.2rem 0; }
    .answer { font-size:1.25rem; background:#F8FAFC; border:1px solid #E2E8F0; padding:1rem; border-radius:8px; }
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
ss.setdefault("page", "Assistente")
ss.setdefault("selected", None)
ss.setdefault("last_task", None)
ss.setdefault("last_trace", None)


def open_card(card_id: str) -> None:
    ss.page, ss.selected = "Memoria del reparto", card_id


# --- sidebar -------------------------------------------------------------
with st.sidebar:
    st.title("🛠️ Il Veterano")
    st.caption("Memoria di reparto visibile e revisionabile")
    st.radio("Schermata", ["Assistente", "Memoria del reparto"], key="page")
    m = llm.mode()
    st.markdown(f"**Modalità:** {'🟢 live · ' + llm.model_id() if m == 'live' else '⚪ offline (percorso deterministico)'}")
    st.caption("Scenario interamente sintetico (P-17, P-22): non sono istruzioni operative reali.")
    if st.button("↺ Ripristina demo"):
        store.reset()
        store.load_fixtures(FIXTURES)
        ss.selected, ss.last_task, ss.last_trace = None, None, None
        st.rerun()


# --- Assistente ----------------------------------------------------------
def page_assistant() -> None:
    st.header("Assistente")
    st.caption("Risponde solo da schede pubblicate, con fonte e variante compatibile. Altrimenti dice perché non risponde.")
    with st.form("ask", clear_on_submit=False):
        q = st.text_input("Domanda dell'operatore", value="Come controllo la P-17 variante A?")
        sent = st.form_submit_button("Chiedi", type="primary")
    if sent and q.strip():
        with st.spinner("Controllo le schede…"):
            ss.last_trace = assistant.answer(q, store, previous_task=ss.last_task)
        if ss.last_trace.task_id:
            ss.last_task = ss.last_trace.task_id
    t = ss.last_trace
    if t:
        st.markdown(f"**{OUTCOME_LABEL[t.rule_outcome]}** · compito: `{t.task_id}` · variante: `{t.context}` · {t.mode}")
        st.markdown(f"<div class='answer'>{t.answer}</div>", unsafe_allow_html=True)
        st.write("")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("**Schede usate**")
            for cid, v in t.used_cards or []:
                st.button(f"📄 {cid} v{v}", key=f"u-{cid}-{v}", on_click=open_card, args=(cid,))
            if not t.used_cards:
                st.write("nessuna")
        with cols[1]:
            st.markdown("**Schede considerate**")
            for cid, v in t.candidate_cards or []:
                c = store.latest(cid)
                st.button(f"{cid} v{v} · {c.status}", key=f"c-{cid}-{v}", on_click=open_card, args=(cid,))
            if not t.candidate_cards:
                st.write("nessuna")
    with st.expander("Traccia delle ultime risposte"):
        for tr in store.traces(15):
            used = ", ".join(f"{c} v{v}" for c, v in tr.used_cards) or "—"
            st.markdown(f"`{tr.asked_at:%H:%M:%S}` **{tr.question}** → {OUTCOME_LABEL[tr.rule_outcome]} · usate: {used}")


# --- Memoria del reparto ---------------------------------------------------
def render_field(card: Card, name: str) -> None:
    fv = card.field(name)  # type: ignore[arg-type]
    css = "field-missing" if fv.missing else "field-ok"
    value = fv.value if not fv.missing else "MANCANTE — non lo inventiamo"
    st.markdown(f"<div class='{css}'><b>{FIELD_LABEL[name]}</b><br>{value}</div>", unsafe_allow_html=True)
    for sid in fv.segment_ids:
        seg = store.segment(sid)
        st.markdown(f"<div class='quote'>“{seg.text}” — {seg.expert} · <code>{sid}</code></div>", unsafe_allow_html=True)


def card_detail(card: Card) -> None:
    st.subheader(f"{card.card_id} · v{card.version} · {STATUS_BADGE[card.status]}")
    st.caption(f"Compito `{card.task_id}` · dichiarato da {card.expert}" + (f" · pubblicata da {card.reviewer} il {card.reviewed_at:%d/%m %H:%M}" if card.reviewer else ""))
    for name in ("context", "action", "rationale"):
        render_field(card, name)
    if card.conflicts:
        st.warning("Conflitto nello stesso contesto con: " + ", ".join(card.conflicts))

    gaps = detect_gaps(card)
    if gaps and card.status != "respinta":
        st.markdown("### Lacune → domande all'esperto")
        for g in gaps:
            with st.form(f"gap-{card.card_id}-{g.field}-{card.version}"):
                st.markdown(f"**{g.rule}** · {g.question}")
                ans = st.text_input("Risposta dell'esperto (parole esatte)", key=f"ans-{g.field}-{card.version}")
                if st.form_submit_button("Collega la risposta alla scheda"):
                    if ans.strip():
                        val, _ = extract.propose_value(g.field, ans, card)
                        seg = Segment(
                            segment_id=store.next_segment_id("SRC-LIVE"), source_id="SRC-LIVE",
                            expert=card.expert, text=ans.strip(), recorded_at=datetime.now(),
                        )
                        store.answer_with_field(card.card_id, g.field, seg, value=val)
                        st.rerun()

    st.markdown("### Revisione")
    ok, reason = can_publish(card)
    c1, c2 = st.columns([2, 1])
    reviewer = c1.text_input("Responsabile", value="Capo reparto (simulato)", key=f"rev-{card.card_id}")
    if c2.button("✅ Pubblica", disabled=not ok, type="primary", key=f"pub-{card.card_id}-{card.version}"):
        store.publish(card.card_id, reviewer)
        st.rerun()
    if not ok:
        c2.caption(f"Non pubblicabile: {reason}")
    if card.status == "bozza" and st.button("Respingi", key=f"rej-{card.card_id}-{card.version}"):
        store.reject(card.card_id, reviewer)
        st.rerun()

    with st.expander(f"Cronologia ({len(store.history(card.card_id))} versioni)"):
        for h in store.history(card.card_id):
            st.markdown(
                f"**v{h.version}** · {STATUS_BADGE[h.status]} · contesto: {h.context.value or '—'} · "
                f"perché: {h.rationale.value or '—'}" + (f" · revisore: {h.reviewer}" if h.reviewer else "")
            )


def new_story_box() -> None:
    with st.expander("➕ Nuovo racconto di un esperto"):
        with st.form("story"):
            expert = st.text_input("Esperto", value="Esperto 2 (simulato)")
            story = st.text_area("Racconto (testo o trascrizione)", height=120,
                                 placeholder="Sulla P-30 prima di montare la guarnizione la ungo con il grasso blu. Altrimenti si pizzica e perde.")
            if st.form_submit_button("Estrai la scheda") and story.strip():
                n = len(store.all_latest()) + 1
                src = f"SRC-{datetime.now():%H%M%S}"
                known = sorted({c.task_id for c in store.all_latest()})
                with st.spinner("Estraggo campi e fonti…"):
                    card, segs, used = extract.extract_card(story, expert, src, f"CARD-NEW-{n:02d}", known)
                for s in segs:
                    store.add_segment(s)
                store.save_card(card)
                ss.selected = card.card_id
                st.toast(f"Bozza {card.card_id} creata ({used})")
                st.rerun()


def page_memory() -> None:
    st.header("Memoria del reparto")
    st.caption("Ogni scheda: cosa fare, in quale variante, perché, e le parole esatte dell'esperto da cui viene.")
    new_story_box()
    cards = store.all_latest()
    tasks = sorted({c.task_id for c in cards})
    f1, f2 = st.columns(2)
    task_f = f1.selectbox("Compito", ["tutti", *tasks])
    status_f = f2.selectbox("Stato", ["tutti", "bozza", "pubblicata", "respinta"])
    shown = [c for c in cards if (task_f == "tutti" or c.task_id == task_f) and (status_f == "tutti" or c.status == status_f)]

    left, right = st.columns([1, 2])
    with left:
        for c in shown:
            miss = f" · manca: {', '.join(c.missing_fields)}" if c.missing_fields else ""
            st.button(
                f"{STATUS_BADGE[c.status]} {c.card_id} v{c.version}\n{c.task_id}{miss}",
                key=f"sel-{c.card_id}", on_click=open_card, args=(c.card_id,), use_container_width=True,
            )
    with right:
        if ss.selected:
            try:
                card_detail(store.latest(ss.selected))
            except KeyError:
                st.info("Seleziona una scheda.")
        else:
            st.info("Seleziona una scheda a sinistra.")


if ss.page == "Assistente":
    page_assistant()
else:
    page_memory()
