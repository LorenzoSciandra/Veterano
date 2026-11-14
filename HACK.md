# HACK.md — Il Veterano (candidato)

> Fonte unica di verità del team per la giornata. Ogni fatto ha un marker: `[verified: fonte]` · `[declared]` · `[unverified]`.
> Una sezione vuota dice `MISSING — serve prima di <fase>`.

Team: Lorenzo Sciandra, Lorenzo Brescia · Builder: MISSING · Business owner: MISSING · Presenter: MISSING
Clock: video 12:30 · pitch 16:45 · Credito: $25 (chiave dalle 10:30) · Rubrica: SKILL.md §2a, track candidato 3b-memory-for-people

## Selection criteria (scritti prima delle idee)
1. Si mostra end to end oggi, in due persone.
2. Il core risponde a una domanda della sfida con un meccanismo funzionante (memoria visibile, regola superata, perché di una decisione).
3. Una persona reale sentirebbe la differenza (sentiment pesa 20 al gate 1 per il track 3b).

## Shortlist and gate
| Idea | Potential | Readiness | Flags | Verdict |
|------|-----------|-----------|-------|---------|
| 6 · Il Veterano (oggi, nessun contatto reale) | 49 [P1 3 · P2 2 · P3 4 · P4 2 · P5 1] | 71 [R1 4 · R2 3 · R3 3 · R4 4] | median_idea | TOY |
| 6 · Il Veterano (con 1 tecnico reale sentito oggi) | 57 [P5 3] | 75 [R3 4] | ok | TOY |
| 6 · Il Veterano su un verticale con costo qualità/sicurezza e accesso reale | da riscorare: serve P1 4 + P4 3 + P5 3 per arrivare a ~65 | | | NARROW→BUILD IT se l'accesso è reale |

Motivi per asse: P1 3, lavoro ricorrente con persone dedicate [declared + unverified Excelsior] · P2 2, categoria con AI-native finanziati (Interloom) e incumbent di work instructions [verified] · P3 4, la risposta si verifica contro scheda pubblicata, versione e variante · P4 2, meccanismo copiabile in uno sprint, nessuna ontologia di dominio ancora · P5 1, nessuna esperienza di dominio dichiarata · R1 4, flusso chiaro nel PDF · R2 3, dati sintetici realistici · R3 3, mentor e proxy · R4 4, in pieno sul track, ruoli ancora da assegnare.
Calcolo: scripts/score.py (autovalutazione, non la rubrica della giuria).

Chosen: Il Veterano · track 3b-memory-for-people — decisione del team 10:08 [declared]. Il verdetto TOY non è un'override: è il segnale che serve un verticale reale (vedi GATE in chat).

## The 8hack canvas

### Q1 · Problem
MISSING — serve prima di GATE (numero anche grezzo, sarà [declared]).

### Q2 · Focus
MISSING — serve prima di BUILD.

### Q3 · UVP to test
MISSING — serve prima di BUILD.

### Q4 · USPs
MISSING — dopo il gate. Vincolo dal landscape: ogni USP deve battere Interloom, Poka/SwipeGuide o Guru, non solo lo status quo.

### Q5 · Single points of failure
MISSING — serve prima del feature freeze.

### Q6 · First things to build
MISSING — serve prima di BUILD.

### Q7 · Target audience
MISSING — conteggio bottom-up PMI manifatturiere (ISTAT) non ancora verificato.

### Q8 · Moat technologies
MISSING — vedi references/moat.md.

## Landscape (as of 2026-11-14)

LANDSCAPE · Il Veterano · as of 2026-11-14
Method: 6 ricerche web (job, AI-native + funding, incumbent work instructions, native-feature, Italia/sentiment, verifica e citazione), ~10 min. Prezzi degli incumbent quasi tutti a preventivo; nessuna cifra ISTAT/INPS diretta trovata.

Market: in Italia la difficoltà a reperire profili tecnici è salita dal 45% (2023) al 48% (2024) secondo Excelsior, citato da fonte secondaria [unverified: blog.se.com]. Intesa Sanpaolo Research segnala attenzione crescente al trasferimento del sapere dei senior [verified: group.intesasanpaolo.com]. Rischio più acuto nelle micro e piccole imprese [unverified: quifinanza su dati CGIA]. Conteggio bottom-up: MISSING.

Alternatives
| Nome | Cosa fa | Segmento | Prezzo | Trazione | Perché non risolve il NOSTRO focus | Marker |
|------|---------|----------|--------|----------|-------------------------------------|--------|
| Interloom (Monaco) | Cattura il sapere tacito da ticket, email e trascrizioni in un "context graph" che fa da memoria per agenti AI | Enterprise operations (cliente Lenze) | n.d. | Seed da €14,2M, marzo 2026 | Ingestione passiva di tracce esistenti; nessun colloquio guidato dalle lacune; target enterprise | [verified: eu-startups.com] |
| Poka | Video dell'operatore → istruzioni passo-passo con GenAI, revisione dell'esperto | Manifattura, connected worker | n.d. | n.d. | L'output è una SOP; nessuna regola di applicabilità per variante; nessuna risposta legata alla versione | [declared: vendor, via emerj.com] |
| Workerbase | Cattura hands-free delle fix → SOP visuali con AI | Manifattura (cita Siemens e Porsche) | n.d. | n.d. | Come Poka | [declared: vendor] |
| Augmentir · SwipeGuide/L2L · Dozuki | Istruzioni di lavoro digitali, generazione con AI da documenti e video | Manifattura mid/enterprise | A preventivo; SwipeGuide da €649 su listino terzo | Dozuki è il più consolidato | Strumenti di authoring, non memoria governata con lacune e conflitti | [unverified: manual.to, G2] |
| Guru | Schede verificate; risposte AI con citazione della scheda di origine | Knowledge base aziendale (sales, support) | A preventivo | Affermato | Le sue stesse guide dicono che schede verificate e non verificate hanno lo stesso peso nelle risposte; non industriale; nessun contesto di variante | [verified: help.getguru.com] |
| Status quo | Affiancamento del senior, raccoglitori, "chiedi a Mario" | Ovunque | Ore del senior | Ovunque | Non scala e sparisce con la pensione | [declared] |

Native-feature risk: la memoria di Claude si può vedere e modificare, organizzata per argomenti da agosto 2026 [unverified: blog terzi]. Gli owner Team/Enterprise però non vedono né modificano le memorie dei singoli membri [unverified: blog terzi]. Quindi la memoria nativa è personale, non una memoria di reparto revisionata da un responsabile. Rischio medio.

Recent moves: Interloom seed €14,2M (03/2026) [verified]; Transfyr seed $25M per il sapere tacito nei laboratori (08/2026) [unverified: wowtale]; Pickmybrain $2,1M [unverified].

Gaps: numero di PMI manifatturiere 10–49 addetti (ISTAT, da verificare); prezzi reali degli incumbent; nessuna valutazione indipendente dei risultati di questi strumenti.

So what:
- P2 Innovation void: la categoria "catturare il sapere dei senior" ha già soldi e prodotti. Non è un vuoto. Il vuoto possibile è stretto: colloquio guidato dalle lacune + applicabilità per variante + l'assistente risponde solo da schede pubblicate e lo dimostra.
- P4 Defensibility: bassa sul meccanismo (copiabile in uno sprint da Guru o Interloom); può crescere solo con l'ontologia di dominio validata e i dati di un verticale.
- USP da battere: Guru (schede verificate non pesate di più nelle risposte), Poka/SwipeGuide (SOP senza contesto di variante), Interloom (enterprise, ingestione passiva).
- Willingness to invest: segnale positivo, perché investitori pagano già questa categoria (Interloom).

Sources: eu-startups.com/2026/03/german-startup-interloom-lands-e14-2-million-seed-funding-for-ai-agent-knowledge-infrastructure · emerj.com/converting-tribal-knowledge-into-operational-performance · workerbase.com/blog/ai-in-manufacturing-knowledge-management · manual.to/compare/work-instruction-software-pricing · help.getguru.com/docs/getting-ai-generated-answers · blog.se.com/it/service/2026/08/27/inverno-demografico-carenza-competenze-futuro-manifattura-servizi-digitali · group.intesasanpaolo.com/it/research/area-media/macro-italia/2026/competenze-manifattura-tecnici-specializzati · quifinanza.it/lavoro/lavoratori-anziani-cgia-mestre-2026/954792 · blog.memoryplugin.com/claude-vs-chatgpt-vs-gemini-memory

## Evidence log
| When | Who (ruolo, reale o proxy) | Citazione o osservazione | Assunzione: confermata / smentita / incerta |
|------|----------------------------|--------------------------|---------------------------------------------|

## Verification log
| When | Cosa ha prodotto un agente | Cosa ha controllato un umano, e come | Errore dell'agente e come l'abbiamo preso |
|------|----------------------------|--------------------------------------|-------------------------------------------|
| 10:41 | Nucleo deterministico (regole R1-R3, store versionato) + 12 casi attesi | DA FARE: Sciandra rilegge i 12 casi attesi in checks/cases.json. Li ha scritti l'agente: 11/11 al primo colpo resta sospetto finché un umano non li controlla | — |
| 10:44 | Interpretazione della domanda con il modello | Test end to end con il modello reale e lettura dell'output grezzo | Con max_tokens=150 il modello spendeva tutto in ragionamento e restituiva testo vuoto (finish_reason=length), e il sistema ripiegava in silenzio sull'offline. Trovato leggendo l'output grezzo; fix: minimo 1200 token ed errore esplicito su risposta vuota |
| 10:44 | Assistente su domanda di seguito ("E per la variante B?") | Stesso test end to end | La domanda di seguito perdeva il compito e dava "compito sconosciuto" invece di "nessuna scheda per la variante B". Fix: il compito della domanda precedente passa come contesto |
| 10:45 | UI Streamlit | Percorso demo in 6 passi guidato automaticamente dalla UI (AppTest), offline | Nessuna eccezione; esiti attesi a ogni passo |

## Checkpoints
- 1st: MISSING
- 2nd (feature freeze): MISSING
