# Chatbot — Giorgio Fede Sindaco 2026

Chatbot per rispondere alle domande dei cittadini sul programma politico della coalizione **"Progettiamo Insieme la San Benedetto del Futuro"** per le Elezioni Comunali 2026 di San Benedetto del Tronto.

Candidato sindaco: **Giorgio Fede**, sostenuto da Partito Democratico, Movimento 2050, Alleanza Verdi Sinistra/PSI, Cambia San Benedetto, Progetto Civico Sambenedettese.

---

## Come funziona

Il programma di coalizione (39 pagine PDF) viene caricato all'avvio del server e incluso interamente nel system prompt inviato al modello AI. Quando un utente pone una domanda, il testo completo del programma è già disponibile come contesto, senza necessità di un sistema di ricerca o un database vettoriale.

```
[PDF programma]
      │
      ▼
[pypdf estrae il testo]
      │
      ▼
[system prompt  →  Mistral Large]  ←  [domanda utente]
                        │
                        ▼
                  [risposta in chat]
```

### Stack

| Componente | Tecnologia |
|---|---|
| Backend | Python · Flask |
| Modello AI | Mistral Large (`mistral-large-latest`) |
| Lettura PDF | pypdf |
| Frontend | HTML · CSS · JavaScript vanilla |
| Rendering markdown | marked.js |
| Server di produzione | Gunicorn |
| Deploy | Railway |

---

## Guardrail anti-allucinazione

Il modello è vincolato da istruzioni esplicite nel system prompt:

- risponde **solo** sulla base del testo del programma
- **cita sempre la sezione** da cui proviene l'informazione
- dichiara esplicitamente quando un argomento **non è presente** nel programma
- non fa inferenze o estrapolazioni

Viene inoltre usata `temperature=0` per rendere le risposte deterministiche e fedeli al testo sorgente.

---

## Struttura del progetto

```
chatbot-fede/
├── app.py                 # server Flask + logica AI
├── programma.pdf          # programma di coalizione (sorgente)
├── requirements.txt       # dipendenze Python
├── Procfile               # comando di avvio per Railway/Render
├── .gitignore
└── templates/
    └── index.html         # interfaccia chat (HTML/CSS/JS)
```

---

## Avvio in locale

```bash
# Installa le dipendenze
pip install -r requirements.txt

# Avvia il server
MISTRAL_API_KEY=sk-... python3 app.py
```

Apri **http://localhost:5001** nel browser.

La chiave API Mistral si ottiene su [console.mistral.ai](https://console.mistral.ai).

---

## Deploy su Railway

1. Crea un repo GitHub e fai push del progetto
2. Su [railway.app](https://railway.app): **New Project → Deploy from GitHub repo**
3. Nelle **Variables** del servizio aggiungi `MISTRAL_API_KEY`
4. Railway rileva il `Procfile` e fa il deploy automaticamente
