# 🤖 AI-Powered Customer Support Chatbot

A complete, beginner-friendly chatbot web application built with **Python**,
**Flask**, **NLTK**, and **scikit-learn**. It answers customer-support and
FAQ-style questions, understands different phrasings of the same question,
remembers basic conversation context, and logs every conversation to a
local **SQLite** database.

No paid APIs are used anywhere — everything runs 100% locally.

---

## 📁 Project Structure

```
chatbot_app/
│
├── app.py               # Flask application: routes, sessions, error handling
├── nlp_engine.py         # NLP "brain": preprocessing, intent detection, responses
├── database.py           # SQLite setup + functions to log/read conversations
├── faq_data.py            # Predefined FAQ dataset (intents, patterns, responses)
├── init_db.py             # Standalone script to initialize the database
├── requirements.txt       # Python dependencies
├── README.md               # This file
│
├── templates/
│   └── index.html          # Chat web page (HTML)
│
├── static/
│   ├── style.css            # Responsive chat UI styling
│   └── script.js              # Frontend logic (sending/receiving messages)
│
└── chatbot.db              # SQLite database (auto-created on first run)
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.9 or newer installed on your machine.

### 2. Get the project files
Place all the project files in a folder (e.g. `chatbot_app/`), keeping the
folder structure shown above.

### 3. (Recommended) Create a virtual environment
```bash
cd chatbot_app
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Download the required NLTK data
The app tries to auto-download the NLTK data it needs (`punkt`, `stopwords`,
`wordnet`, `omw-1.4`) the first time it runs. If your environment blocks
that automatic download, run this once manually:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### 6. Initialize the database (optional — happens automatically too)
```bash
python init_db.py
```

### 7. Run the application
```bash
python app.py
```

You should see output like:
```
[database] Database ready at: .../chatbot.db
 * Running on http://127.0.0.1:5000
```

### 8. Open the chatbot
Go to **http://127.0.0.1:5000** in your browser and start chatting!

---

## 🧠 How the NLP & Response Generation Works

This chatbot uses a **retrieval-based** approach (as opposed to a
generative model like GPT). That means it doesn't "write" new sentences —
instead, it picks the best matching answer from a predefined FAQ dataset
(`faq_data.py`). This makes it fast, predictable, explainable, and perfect
for customer support, where answers need to be accurate and consistent.

### Step 1 — Text Preprocessing (NLTK)
Every message (both the FAQ patterns and the user's input) goes through the
same cleanup pipeline in `nlp_engine.py`, using **NLTK**:

1. **Lowercasing** — `"How Much Does It Cost?"` → `"how much does it cost?"`
2. **Punctuation removal**
3. **Tokenization** — splitting text into individual words:
   `["how", "much", "does", "it", "cost"]`
4. **Stop-word removal** — common, low-information words like "how", "does",
   "it", "the", "is" are removed: `["much", "cost"]`
5. **Lemmatization** — words are reduced to their base/dictionary form
   (e.g. "running" → "run", "prices" → "price")

This normalization is what allows the bot to recognize that *"How much does
it cost?"*, *"what's the price?"*, and *"pricing plans"* are all really
asking about the same thing — even though the wording is completely
different.

### Step 2 — Intent Detection with TF-IDF + Cosine Similarity
Once text is cleaned, we need a way to measure how *similar* the user's
message is to each known FAQ question. We do this with:

- **TF-IDF (Term Frequency–Inverse Document Frequency)**: converts each
  cleaned sentence into a numeric vector, where words that are distinctive
  (appear in few patterns) get more weight than common words that appear
  everywhere.
- **Cosine Similarity**: measures the angle between two vectors, giving a
  score from 0 (completely different) to 1 (identical meaning/wording).

For every user message, the chatbot compares it against **every** pattern
in the FAQ dataset and finds the closest match. Patterns are grouped by
"intent" (e.g. `account_password`, `refund_policy`), and we take the best
score per intent.

- If the best score is **high** (≥ 0.35), the bot is confident and replies
  directly with the matching FAQ answer.
- If the best score is **low** (< 0.15), the bot doesn't understand the
  question and returns a friendly fallback message asking the user to
  rephrase.

### Step 3 — Basic Conversation Context
To handle short follow-up questions (e.g. user asks *"what's the price?"*
then follows up with *"and for the pro plan?"*), the app remembers the
**last detected intent** in the Flask session. When a new message scores
only *moderately* well, the bot gives a small similarity "bonus" to
whichever topic was just being discussed — biasing the match toward
continuing the same conversation thread instead of guessing from scratch
each time.

### Step 4 — Response Selection
Each intent in `faq_data.py` can have multiple possible responses. Once an
intent is chosen, the bot picks one of its responses at random, so replies
feel a little more natural and less robotic on repeat visits.

### Why this approach (and not a large language model)?
- **No cost, no API keys, fully offline** — works with just NLTK + scikit-learn.
- **Predictable & controllable** — for customer support, you want guaranteed,
  approved answers, not an LLM potentially inventing incorrect information.
- **Easy to extend** — adding a new FAQ topic is as simple as adding a new
  entry to `faq_data.py`; no retraining or fine-tuning required.
- **Beginner-friendly** — the whole pipeline (clean text → vectorize →
  compare → respond) is transparent and easy to follow, step by step.

> 💡 **Want to go further?** The same `nlp_engine.py` module could be
> swapped to use a Hugging Face Transformers sentence-embedding model
> (e.g. `sentence-transformers/all-MiniLM-L6-v2`) instead of TF-IDF for
> even better semantic matching — the rest of the app (Flask routes,
> database logging, frontend) would not need to change at all, since
> `get_response()` keeps the same interface.

---

## 🗄️ Database Schema

Every exchange is logged to `chatbot.db`, table `conversations`:

| Column         | Type    | Description                          |
|----------------|---------|---------------------------------------|
| `id`           | INTEGER | Auto-incrementing primary key         |
| `user_message` | TEXT    | What the user typed                   |
| `bot_response` | TEXT    | What the bot replied                  |
| `intent`       | TEXT    | Detected intent/topic (e.g. `greeting`) |
| `timestamp`    | TEXT    | When the message was logged (ISO 8601) |

You can inspect it with any SQLite browser, or from Python:
```python
from database import get_recent_conversations
for row in get_recent_conversations(20):
    print(row)
```

---

## 🛠️ Customizing / Extending the Chatbot

- **Add new FAQ topics**: open `faq_data.py` and add a new dictionary with
  a `tag`, a list of `patterns` (different phrasings), and one or more
  `responses`. No other code changes are needed.
- **Tune matching sensitivity**: adjust `HIGH_CONFIDENCE`, `LOW_CONFIDENCE`,
  and `CONTEXT_BONUS` in `nlp_engine.py`.
- **Change the fallback replies**: edit `FALLBACK_RESPONSES` in
  `nlp_engine.py`.
- **View chat history in the browser**: you could add an `/history` route
  in `app.py` that calls `get_recent_conversations()` and renders it as an
  admin page.

---

## ❗ Error Handling Included

- Empty or whitespace-only messages are rejected with a clear error (both
  client-side in JavaScript and server-side in Flask).
- Non-JSON or malformed requests return a `400` error with a helpful message.
- Overly long messages (> 500 characters) are rejected.
- Any unexpected exception during NLP processing is caught so the server
  never crashes — the user gets a graceful "something went wrong" message
  instead.
- Database logging failures don't prevent the chatbot from still replying
  to the user.

---

## 📦 requirements.txt

```
Flask==3.0.3
nltk==3.9.1
scikit-learn==1.5.2
numpy==1.26.4
```

Enjoy building on top of your chatbot! 🚀
