# Il Veterano

Memoria di reparto visibile e revisionabile: il sapere dei tecnici esperti diventa schede con fonte, variante e motivazione; un responsabile le revisiona e pubblica; l'assistente risponde solo da schede pubblicate e applicabili, e mostra quale versione ha usato.

Hackathon "AI brain for industry", KVA, Torino, 14 novembre 2026 · track 3b-memory-for-people · team Sciandra & Brescia.

- Scenario della demo: **interamente sintetico** (pezzo P-17, varianti A/B). Non sono istruzioni operative reali.
- Contratto tecnico: [CONTRACT.md](CONTRACT.md) · Canvas del progetto: [HACK.md](HACK.md)
- Modelli e strumenti AI usati: Claude (Opus 5.5) in Claude Code come agente di sviluppo; nel prodotto `anthropic/claude-haiku-5.5` via Vercel AI Gateway.

## Avvio

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # inserire AI_GATEWAY_API_KEY, oppure VETERANO_OFFLINE=1
.venv/bin/streamlit run app.py
```
