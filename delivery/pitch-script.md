# Show-off · 5 minuti (3 di pitch e demo, 2 di domande)

Ruoli: **Brescia parla, Sciandra clicca.** Prima di iniziare: app aperta su «Chiedi», scenario ripristinato (Schede → Strumenti demo → Ripristina), zoom del browser al 125%, notifiche spente. Il video di riserva è `delivery/out/idea.mp4`.

## Copione (3:00)

| Tempo | Brescia dice | Sciandra fa |
|---|---|---|
| 0:00–0:20 | «Un collaudatore con trent'anni di reparto va in pensione a dicembre. Quello che sa, quale riflesso su un pezzo è un difetto, non è scritto da nessuna parte. Il Veterano serve a non perderlo.» | Schermo sull'app |
| 0:20–0:40 | «Il nuovo operatore chiede come controllare la P-17 variante A.» | Chiedi: *Come controllo la P-17 variante A?* → risposta arancione |
| | «Non risponde. C'è un'istruzione dell'esperto, ma nessuno l'ha approvata. Non inventa.» | |
| 0:40–1:15 | «Ecco cosa ha detto l'esperto. Mancano due cose: per quale variante vale, e perché. Il sistema gliele chiede, una alla volta.» | Completa l'istruzione → risposta R1: *Alla variante A, per la B usiamo un'altra scheda.* → Salva. R2: *Così non segno come buono un pezzo con un difetto che a occhio non si vede.* → Salva |
| 1:15–1:30 | «Il capo reparto rilegge accanto alle parole dell'esperto e approva.» | Approva e pubblica |
| 1:30–1:55 | **Il momento chiave.** «Stessa domanda.» … «Ora risponde, e dice da dove: scheda approvata, versione 4. E per la variante B?» … «Nessuna risposta inventata.» | Chiedi la stessa domanda → verde. Poi *E per la variante B?* → arancione |
| 1:55–2:15 | «La memoria cambia nel tempo. Il serraggio della P-17 è cambiato a ottobre: si vede cosa c'era prima e da quando vale il nuovo. E quando due esperti dicono cose diverse, decide una persona.» | Schede → Serraggio (riga «Prima era») → Sbavatura P-22 bozza → contrasto fianco a fianco (non cliccare) |
| 2:15–2:35 | «Business: un pilota di otto settimane a 4.000 euro, poi 390 euro al mese per reparto. Sono stime nostre, non ancora verificate con un cliente.» | — |
| 2:35–2:50 | «Abbiamo sviluppato con Claude Opus 5.5 e nel prodotto usiamo Claude Haiku. Le regole che decidono quando rispondere sono codice, non modello: 15 casi di test su 15.» | — |
| 2:50–3:00 | «Prossimo test: tre capi reparto per una settimana. Se meno di due approvano cinque schede, cambiamo il flusso. L'esperto va in pensione. Il suo sapere, no.» | — |

**Se la demo dal vivo si blocca:** «Vi mostriamo la stessa esecuzione registrata stamattina», poi si avvia `idea.mp4` dal secondo 18.

## Domande probabili: una riga ciascuna

- **Chi è l'utente, chi paga?** Usano il sistema operatore, esperto e capo reparto; paga il responsabile operativo della PMI.
- **Cosa è reale e cosa no?** Il software e il modello sono reali e girano dal vivo. Lo scenario (pezzi, varianti) è simulato e dichiarato.
- **Quale modello, e come lo controllate?** Claude Haiku 5.5 estrae e formula. Cosa usare lo decidono le regole in codice, verificate da 15 casi di test.
- **Cosa ha sbagliato l'agente?** Risposte vuote per limite di token, e il compito perso nelle domande di seguito. Trovati leggendo l'output grezzo, corretti.
- **Perché non basta la memoria di ChatGPT o Claude?** È personale: non c'è approvazione di reparto, non ci sono fonti, non c'è una vista condivisa.
- **E Interloom, Poka, Guru?** Catturano o generano contenuti. Nessuno lega la risposta a un'approvazione e a una variante, e Guru pesa uguale schede verificate e no.
- **Cosa è difficile da copiare?** Oggi poco. Domani lo schema di dominio validato e lo storico delle approvazioni di ogni reparto.
- **E se il capo reparto non ha tempo?** È la nostra ipotesi più rischiosa, ed è il test della prossima settimana. Il flusso gli chiede solo di approvare, non di scrivere.
- **I dati escono dall'azienda?** Nel prototipo passano da un modello in cloud. In produzione si può usare un modello installato in azienda: le regole non dipendono dal modello.
- **Il numero che vi fermerebbe?** Meno di 2 capi reparto su 3 che approvano almeno 5 schede in una settimana.
