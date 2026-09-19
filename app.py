"""
app.py
------
The main Flask application. This file wires everything together:

  - Serves the chat web page (templates/index.html)
  - Exposes a POST /chat endpoint that the frontend JavaScript calls with
    each user message
  - Uses nlp_engine.py to detect intent and generate a response
  - Uses database.py to log every exchange into SQLite
  - Keeps a tiny bit of per-user "context" (the last detected topic) in the
    Flask session, so simple follow-up questions can be understood

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify, session
import os

from database import init_db, log_conversation
from nlp_engine import chatbot_nlp

app = Flask(__name__)

# Secret key is required for Flask sessions (used to remember conversation
# context per browser tab/user). In a real production app, load this from
# an environment variable instead of hard-coding it.
app.secret_key = os.environ.get("CHATBOT_SECRET_KEY", "dev-secret-key-change-me")


@app.route("/")
def index():
    """Render the main chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Receive a JSON payload like {"message": "hi there"} from the frontend,
    run it through the NLP engine, log the exchange, and return the bot's
    reply as JSON.
    """
    # --- Basic error handling for malformed/unexpected input -------------
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    if not isinstance(user_message, str):
        return jsonify({"error": "'message' must be a string."}), 400

    user_message = user_message.strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty. Please type something."}), 400

    if len(user_message) > 500:
        return jsonify({"error": "Message is too long (max 500 characters)."}), 400

    # --- Run the NLP engine ------------------------------------------------
    last_tag = session.get("last_tag")
    try:
        bot_response, tag, confidence = chatbot_nlp.get_response(user_message, last_tag)
    except Exception as exc:  # Catch-all so a bad input never crashes the server
        app.logger.exception("Error while generating chatbot response")
        bot_response = (
            "Sorry, something went wrong on my end while processing that. "
            "Please try again."
        )
        tag = "error"
        confidence = 0.0

    # Remember this turn's topic for the next request (basic context)
    session["last_tag"] = tag

    # --- Log to SQLite -------------------------------------------------
    try:
        log_conversation(user_message, bot_response, tag)
    except Exception:
        app.logger.exception("Failed to log conversation to database")
        # We still return a response to the user even if logging fails.

    return jsonify(
        {
            "response": bot_response,
            "intent": tag,
            "confidence": round(confidence, 3),
        }
    )


@app.route("/reset", methods=["POST"])
def reset_context():
    """Clear the stored conversation context (e.g. when the user clicks 'New chat')."""
    session.pop("last_tag", None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Make sure the database and its table exist before the app starts.
    init_db()
    # debug=True gives helpful auto-reload + error pages during development.
    # Turn this off (debug=False) before deploying anywhere public.
    app.run(debug=True, host="127.0.0.1", port=5000)
