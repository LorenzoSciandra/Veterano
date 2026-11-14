# Interviste SIMULATE (personaggi inventati)

> Tutto ciò che segue è **inventato**: personaggi, aziende, episodi e cifre.
> Serve a tre cose: provare le domande prima delle interviste vere, fornire racconti di esperti alla demo, preparare le risposte del pitch.
> **Non è un'evidenza.** In video, abstract e pitch non si presenta come «abbiamo intervistato». Se si usa, si scrive «scenario simulato».
> Nel registro delle evidenze di HACK.md va solo con il marker `[SIMULATA]`.

## Personaggio 1 · Responsabile qualità (chi compra e chi revisiona)
**Profilo:** Giulia, 44 anni, responsabile qualità in una PMI di componentistica auto, 45 addetti, cintura di Torino. *(inventato)*

- **D: L'ultima volta che un esperto è andato via?** «Lo scorso marzo è andato in pensione il collaudatore più anziano, trentun anni in azienda.»
- **D: Cosa sapeva fare che gli altri no?** «Riconosceva a occhio i difetti di superficie sulle flange. Non c'era scritto da nessuna parte: lui sapeva quale riflesso era un problema e quale no.»
- **D: Cosa è successo dopo?** «Per due mesi abbiamo avuto più resi dal cliente su quel codice. Un lotto intero ci è tornato indietro.»
- **D: Come avete recuperato?** «L'abbiamo richiamato due volte come consulente. Io ho passato ore a scrivere una procedura che poi nessuno leggeva.»
- **D: Quanto tempo dedicheresti a revisionare schede?** «Mezz'ora a settimana sì, se sono già scritte e devo solo dire sì o no. Scriverle da zero no.»

**Frase chiave:** «Non c'era scritto da nessuna parte: lui sapeva quale riflesso era un problema.»
**Obiezione:** il tempo di scrittura. Il Veterano lo toglie, perché lei approva e basta.

## Personaggio 2 · Capo manutenzione
**Profilo:** Marco, 52 anni, capo manutenzione in un'azienda di stampaggio plastica, 30 addetti. *(inventato)*

- **D: L'ultima volta?** «Due anni fa si è licenziato il manutentore delle presse, è andato in un'azienda più grande.»
- **D: Cosa sapeva?** «Le regolazioni della pressa vecchia, la 3. Aveva i suoi trucchi, tipo l'ordine in cui scaldare gli stampi d'inverno.»
- **D: Cosa è successo dopo?** «Fermi più lunghi. Un fermo da mezza giornata a gennaio ci è costato una consegna in ritardo.»
- **D: Come avete recuperato?** «A tentativi, e con il tecnico del costruttore, che costa.»
- **D: Avete provato qualcosa?** «Un quaderno in officina. Dopo tre mesi non lo aggiornava più nessuno.»

**Frase chiave:** «Un quaderno in officina. Dopo tre mesi non lo aggiornava più nessuno.»
**Insegnamento:** l'aggiornamento è il vero problema, ed è il motivo per cui servono versioni e revisione.

## Personaggio 3 · Operatore neoassunto (chi usa l'assistente)
**Profilo:** Luca, 23 anni, operatore CNC da un anno in una PMI meccanica. *(inventato)*

- **D: Quando ti è servito sapere una cosa che nessuno aveva scritto?** «Al primo attrezzaggio da solo. Il foglio diceva una cosa, il collega anziano ne faceva un'altra.»
- **D: Cosa hai fatto?** «Ho chiesto al collega. Mi ha detto "per la variante B no, si fa diverso". Sul foglio la variante non c'era.»
- **D: E se il collega non c'era?** «Avrei seguito il foglio e sbagliato. Infatti una volta è successo: venti pezzi da rifare.»

**Frase chiave:** «Sul foglio la variante non c'era.»
**Insegnamento:** il contesto, cioè la variante, è la lacuna più costosa, ed è esattamente la regola R1.

## Personaggio 4 · Direttore operativo (chi paga)
**Profilo:** Paolo, 58 anni, socio e direttore operativo di una PMI meccanica di precisione, 20 addetti. *(inventato)*

- **D: Quanti esperti escono nei prossimi anni?** «Tre su venti nei prossimi quattro anni. Uno è l'unico che sa fare il collaudo finale.»
- **D: Cosa avete fatto finora?** «Affiancamento. Ma se lo affianco, quello non produce.»
- **D: Cosa ti farebbe dire di no?** «Se devo comprare un altro software che poi nessuno usa. E non voglio che i dati escano dall'azienda.»

**Frase chiave:** «Se lo affianco, quello non produce.»
**Obiezioni da preparare per il pitch:** adozione (il sistema chiede poco tempo e lavora per compito) e riservatezza dei dati.

---

## Tabella per HACK.md (solo con il marker [SIMULATA])

| When | Who | Citazione | Assunzione |
|---|---|---|---|
| 11:15 | [SIMULATA] Responsabile qualità, componentistica auto | «Mezz'ora a settimana sì, se devo solo dire sì o no» | Revisione: plausibile, da verificare con persone reali |
| 11:15 | [SIMULATA] Capo manutenzione, stampaggio | «Dopo tre mesi il quaderno non lo aggiornava nessuno» | Il problema è l'aggiornamento: da verificare |
| 11:15 | [SIMULATA] Operatore neoassunto, CNC | «Sul foglio la variante non c'era» | La lacuna sul contesto è costosa: da verificare |
| 11:15 | [SIMULATA] Direttore operativo, meccanica | «Se lo affianco, quello non produce» | Il costo dell'affiancamento è sentito: da verificare |

## Prompt per simulare altre interviste con un LLM (claude.ai)

```
Interpreta un personaggio INVENTATO per un'intervista di prova (Mom Test).
Ruolo: <es. responsabile qualità in una PMI di componentistica auto, 45 addetti, Piemonte>.
Rispondi come risponderebbe una persona reale e un po' scettica: frasi brevi, esempi concreti,
qualche risposta vaga, almeno un'obiezione. Non conosci il nostro prodotto e non devi lodarlo.
Io ti farò queste domande una alla volta:
1. Raccontami l'ultima volta che un collega esperto è andato via.
2. Cosa sapeva fare che gli altri non sapevano?
3. Cosa è successo dopo? Errori, scarti, fermi? Quanto è costato?
4. Come avete cercato di recuperare? Chi ci ha messo il tempo?
5. Chi avrebbe dovuto approvare le istruzioni scritte, e quanto tempo poteva dedicarci?
Alla fine scrivi in una riga: "PERSONAGGIO SIMULATO: non è un dato reale".
```
