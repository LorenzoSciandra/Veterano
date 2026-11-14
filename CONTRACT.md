# Il Veterano — contratto condiviso tra agenti

Questo file è la fonte di verità per ogni agente che scrive codice. Se un agente vuole cambiare un nome, un campo o una firma qui sotto, si ferma e lo chiede a un umano.

Scenario della demo: interamente **sintetico** (pezzo P-17, varianti A/B). Non sono istruzioni operative reali.

## Stack

- Python 3.13, Streamlit, SQLite (file locale `data/veterano.db`), pydantic v2, SDK `openai`.
- Modello: Vercel AI Gateway, endpoint OpenAI-compatibile `https://ai-gateway.vercel.sh/v1`. Chiave in `AI_GATEWAY_API_KEY`, letta solo da variabile d'ambiente (`.env` è escluso da git).
- Modello di default: `anthropic/claude-haiku-5.5`, impostabile con `VETERANO_MODEL`.
- Modalità offline: `VETERANO_OFFLINE=1` usa le fixture in `data/fixtures/` al posto del modello. La UI mostra sempre in quale modalità gira.

## Layout

```
app.py                      Streamlit: due pagine, "Memoria del reparto" e "Assistente"
veterano/models.py          modelli pydantic (sotto)
veterano/store.py           persistenza SQLite: schede versionate, segmenti, eventi, tracce
veterano/rules.py           regole deterministiche R1, R2, R3 (nessuna chiamata al modello)
veterano/llm.py             unico punto che chiama il modello; timeout 20 s; output JSON validato
veterano/extract.py         racconto → bozza di scheda (usa llm.py, fallback fixture)
veterano/assistant.py       domanda → schede applicabili → risposta o rifiuto motivato + traccia
data/fixtures/*.json        scenario P-17 e risposte del modello pre-registrate per l'offline
checks/cases.json           12 casi con risposta attesa, scritti da un umano
checks/run_checks.py        stampa "passed/total" e i casi falliti
```

## Ontologia minima (classi e relazioni)

Classi: Esperto, Compito, Contesto (variante/condizione), Accorgimento (= scheda), Evidenza (segmento di fonte), Revisione.
Relazioni: `siApplicaA` (scheda → compito), `valeIn` (scheda → contesto), `motivatoDa` (scheda → rationale), `dichiaratoDa` (scheda → esperto), `supportatoDa` (campo → segmento), `sostituisce` (versione → versione precedente).

Identità (decisa prima del codice):
- Una **scheda** è identificata da `card_id`. Le versioni hanno `version` intero crescente; una nuova versione non cancella la precedente.
- Un **segmento** è identificato da `segment_id` = `<source_id>#<n>`. Il testo del segmento non cambia mai.
- Due schede sono la stessa cosa solo se hanno lo stesso `card_id`. Lo stesso compito in contesti diversi dà schede diverse.

## Modelli (veterano/models.py)

```python
class Segment(BaseModel):
    segment_id: str          # "SRC-001#2"
    source_id: str           # "SRC-001"
    expert: str              # "Esperto 1 (simulato)"
    text: str                # parole esatte dell'esperto
    recorded_at: datetime

class FieldValue(BaseModel):
    value: str | None        # None = mancante, mai inventato
    segment_ids: list[str]   # segmenti che lo supportano; vuoto se value è None

class Card(BaseModel):
    card_id: str             # "CARD-P17-VIS-01"
    version: int             # 1, 2, ...
    status: Literal["bozza", "pubblicata", "respinta"]
    task_id: str             # "P17-controllo-visivo"
    context: FieldValue      # variante/condizione, es. "P-17 variante A"
    action: FieldValue       # cosa fare
    rationale: FieldValue    # perché: quale errore evita o quale esito fa riconoscere
    expert: str
    missing_fields: list[Literal["context", "action", "rationale"]]
    conflicts: list[str]     # card_id in conflitto nello STESSO contesto
    reviewer: str | None
    reviewed_at: datetime | None
    supersedes_version: int | None

class GapQuestion(BaseModel):
    card_id: str
    field: Literal["context", "rationale"]
    rule: Literal["R1", "R2"]
    question: str            # testo deterministico dal template della regola

class AnswerTrace(BaseModel):
    trace_id: str
    asked_at: datetime
    question: str
    task_id: str | None
    context: str | None      # variante richiesta
    candidate_cards: list[tuple[str, int]]   # (card_id, version) considerate
    used_cards: list[tuple[str, int]]        # (card_id, version) usate davvero
    rule_outcome: Literal["answered", "no_published_card", "context_mismatch", "missing_source", "unknown_task"]
    answer: str
    mode: Literal["live", "offline"]
```

## Regole (veterano/rules.py, deterministiche)

- `detect_gaps(card) -> list[GapQuestion]`
  - **R1**, contesto mancante: se `context.value is None` → "A quale variante o condizione si applica: «{action}»?"
  - **R2**, motivazione mancante: se `rationale.value is None` → "Quale errore evita, o quale esito permette di riconoscere: «{action}»?"
- `applicable(cards, task_id, context) -> (list[Card], outcome)`, per la **R3**: tiene solo le schede con `status == "pubblicata"`, con almeno un `segment_id` sotto `action`, e con `context.value` uguale (normalizzato) al contesto richiesto. Se non ne resta nessuna, l'esito dice perché, nell'ordine `unknown_task` → `no_published_card` → `missing_source` → `context_mismatch`.
- `can_publish(card) -> (bool, reason)`: niente pubblicazione se `missing_fields` non è vuoto o se un campo con valore non ha segmenti.

Il modello **non** decide mai l'applicabilità e non colma lacune. Il modello estrae (`extract.py`) e formula la risposta a partire SOLO dalle schede passate dalla R3 (`assistant.py`).

## Store (veterano/store.py)

```python
init_db(path) -> None
add_segment(seg: Segment) -> None
save_card(card: Card) -> None              # inserisce una nuova riga (card_id, version)
latest(card_id) -> Card
all_latest(task_id: str | None = None) -> list[Card]
history(card_id) -> list[Card]
publish(card_id, reviewer) -> Card         # crea version+1 con status pubblicata; rifiuta se can_publish è False
answer_with_field(card_id, field, segment: Segment) -> Card   # risposta dell'esperto a una GapQuestion → nuova versione bozza
save_trace(t: AnswerTrace) -> None
traces() -> list[AnswerTrace]
load_fixtures(dir) -> None                 # popola il DB demo da data/fixtures
```

## Le due schermate (app.py)

1. **Memoria del reparto**: elenco delle schede filtrabile per compito e stato; nel dettaglio di una scheda: campi, segmenti originali evidenziati per campo, lacune con la domanda R1/R2, un campo per la risposta dell'esperto, il pulsante "Pubblica" (disabilitato con il motivo se `can_publish` è falso) e la cronologia delle versioni.
2. **Assistente**: domanda in linguaggio naturale → risposta oppure rifiuto motivato; sotto, sempre: card_id e versione usate, esito della regola, link per aprire la scheda nella memoria. Più l'elenco delle ultime tracce.

## Il percorso della demo (deve funzionare 3 volte di fila)

1. Assistente: "Come controllo P-17 variante A?" → rifiuto `no_published_card`, con la bozza indicata.
2. Memoria: apro la bozza → contesto e motivazione mancanti, evidenziati.
3. Domanda R1 → l'esperto risponde "Alla variante A; per B usiamo un'altra scheda" → nuovo segmento collegato al contesto.
4. Domanda R2 → l'esperto risponde → motivazione collegata.
5. Il responsabile apre i segmenti e pubblica → versione 3, pubblicata.
6. Assistente: stessa domanda → risposta con CARD-P17-VIS-01 v3. "E per la variante B?" → `context_mismatch`.

## Check set (checks/cases.json, 12 casi)

3 completi · 3 con lacune · 2 fuori ambito · 2 in conflitto nello stesso contesto · 2 compatibili perché in contesti diversi.
Se i conflitti restano fuori dall'MVP, i 4 casi relativi si marcano `not_implemented` e si riportano a parte.
