import os
from flask import Flask, render_template, request, jsonify, session
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

Il tuo compito è rispondere alle domande dei cittadini sul programma in modo chiaro, preciso e utile. Rispondi sempre in italiano. Basa le tue risposte esclusivamente sul contenuto del programma qui sotto. Se ti viene chiesto qualcosa che non è nel programma, dillo onestamente. Sii conciso ma completo.

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

    response = client.chat.complete(
        model="mistral-large-latest",
        max_tokens=1024,
        messages=messages,
    )

    assistant_reply = response.choices[0].message.content
    return jsonify({"response": assistant_reply})


@app.route("/reset", methods=["POST"])
def reset():
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Chatbot Giorgio Fede Sindaco - avviato su http://localhost:5001")
    app.run(debug=False, port=5001)
