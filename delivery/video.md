# Video delle 12:30: copione, inquadrature, abstract

VERSIONE FINALE (11:14): nessun volto, nessuna voce, nessun nome (scelta di privacy del team). Video generato da `delivery/video.html` con `delivery/render_video.py`, sulla demo vera registrata da `delivery/record_demo.py`. La versione con le clip di Brescia, qui sotto, è archiviata.

Vincoli: un solo MP4 (H.264 + AAC), al massimo 50 s e 25 MB. Il video non è anonimo: il team si nomina.
Testo detto: circa 105 parole, da tenere sotto i 45 s. Le parti tra ⟦ ⟧ si riempiono con le interviste di Brescia (11:30).

## Copione

| Secondi | Chi / cosa si vede | Testo detto |
|---|---|---|
| 0–12 | Brescia in camera | «Quando un tecnico esperto se ne va, il suo sapere esce con lui. ⟦Citazione reale, es.: "Quando è andato in pensione Mario, per tre mesi abbiamo scartato pezzi che lui avrebbe fermato" — ruolo, settore⟧.» |
| 12–18 | Brescia in camera | «Succede nelle ⟦piccole aziende manifatturiere di settore⟧, dove un compito critico sta nella testa di una o due persone.» |
| 18–38 | Registrazione schermo della demo (automatica) | «Il Veterano intervista l'esperto partendo da ciò che manca: per quale variante vale? perché lo fai? Il capo reparto controlla le parole esatte e pubblica. L'assistente risponde solo da schede pubblicate e dice quale versione ha usato. Se la scheda non c'è, non inventa.» |
| 38–46 | Brescia in camera, oppure cartello finale | «Oggi verifichiamo una cosa sola: se un responsabile dedicherebbe davvero tempo a revisionare queste schede. Sono Lorenzo Brescia, con Lorenzo Sciandra: votateci se volete scoprirlo stasera.» |

## Inquadrature

1. 0–12 s: primo piano di Brescia (telefono in orizzontale, luce frontale). Sottotitolo: la citazione, con ruolo e settore.
2. 12–18 s: stesso piano. Sottotitolo: «⟦N⟧ PMI ⟦settore⟧ in ⟦area⟧» SOLO se il numero è verificato con fonte.
3. 18–24 s: schermo, l'Assistente rifiuta («esiste solo una bozza»).
4. 24–32 s: schermo, la scheda in bozza con contesto e motivazione in rosso; risposte dell'esperto collegate.
5. 32–38 s: schermo, «Pubblica» → v4, poi stessa domanda → risposta con [CARD-P17-VIS-01 v4]; variante B → nessuna scheda.
6. 38–46 s: Brescia, o un cartello «Il Veterano · Sciandra & Brescia · track Memory for people».

La registrazione dello schermo la genera l'agente con un browser automatico che percorre la demo vera (nessun montaggio di schermate finte).

## Abstract (≤1200 caratteri, BOZZA)

Il Veterano rende visibile e revisionabile la memoria di un reparto. Quando un tecnico esperto se ne va, oggi il suo sapere si recupera con affiancamento, raccoglitori e «chiedi a chi c'era». ⟦Citazione reale dalle interviste⟧.
Il Veterano trasforma il racconto dell'esperto in schede con fonte, variante e motivazione. Tre regole deterministiche, non il modello, decidono:
- se manca la variante o il perché, il sistema fa all'esperto una domanda mirata;
- l'assistente usa solo schede pubblicate da un responsabile, con fonte e variante compatibile;
- altrimenti rifiuta e dice perché.
Ogni risposta mostra la scheda e la versione usata.
Track: Memory for people (3b). Scenario della demo sintetico e dichiarato tale.
Ipotesi più rischiosa: un responsabile dedica davvero tempo a revisionare le schede. Criterio di stop: meno di 2 persone su 4 intervistate raccontano un episodio recente e costoso di sapere perso. Oggi: ⟦n su 4⟧.
Strumenti: Claude Opus 5.5 in Claude Code per lo sviluppo; nel prodotto Claude Haiku 5.5 via Vercel AI Gateway; Python, Streamlit, SQLite.
