import os
import json
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from mistralai import Mistral
from pypdf import PdfReader
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

PDF_PATH = os.path.join(os.path.dirname(__file__), "programma.pdf")


def load_program():
    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


PROGRAM_TEXT = load_program()

SYSTEM_PROMPT = f"""Sei un assistente esperto del programma politico della coalizione "Progettiamo Insieme la San Benedetto del Futuro" per le Elezioni Comunali 2026 di San Benedetto del Tronto. Il candidato sindaco è Giorgio Fede, sostenuto da: Partito Democratico, Movimento 2050, Alleanza Verdi Sinistra/PSI, Cambia San Benedetto, Progetto Civico Sambenedettese.

Il tuo compito è rispondere alle domande dei cittadini sul programma. Segui queste regole senza eccezioni:

1. Rispondi SOLO sulla base del testo del programma riportato qui sotto. Non aggiungere informazioni, opinioni o conoscenze esterne.
2. Indica sempre da quale sezione del programma proviene la risposta (es. "Secondo la sezione Ambiente…").
3. Se l'argomento non è trattato nel programma, rispondi esattamente: "Questo argomento non è presente nel programma di coalizione."
4. Non fare inferenze o estrapolazioni oltre quanto scritto esplicitamente.
5. Rispondi sempre in italiano. Sii conciso ma completo.

=== PROGRAMMA DI COALIZIONE ===

{PROGRAM_TEXT}

=== FINE PROGRAMMA ==="""


@app.route("/")
def index():
    session["history"] = []
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Messaggio vuoto"}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history + [{"role": "user", "content": user_message}]

    def generate():
        try:
            with client.chat.stream(
                model="mistral-large-latest",
                max_tokens=1024,
                temperature=0,
                messages=messages,
            ) as stream:
                for chunk in stream:
                    delta = chunk.data.choices[0].delta.content
                    if delta:
                        yield f"data: {json.dumps({'token': delta})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    resp = Response(stream_with_context(generate()), content_type="text/event-stream")
    resp.headers["X-Accel-Buffering"] = "no"
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["Connection"] = "keep-alive"
    return resp


@app.route("/reset", methods=["POST"])
def reset():
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Chatbot Giorgio Fede Sindaco - avviato su http://localhost:5001")
    app.run(debug=False, port=5001)
