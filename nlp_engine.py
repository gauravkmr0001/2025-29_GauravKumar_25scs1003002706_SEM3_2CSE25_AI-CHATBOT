"""
nlp_engine.py
-------------
This is the "brain" of the chatbot. It is responsible for:

1. Text preprocessing (tokenization, lowercasing, stop-word removal, lemmatization)
   using NLTK.
2. Turning FAQ patterns and user messages into numeric vectors using TF-IDF
   (Term Frequency - Inverse Document Frequency), a classic and very effective
   NLP technique for text similarity.
3. Measuring how similar the user's message is to each known FAQ pattern using
   cosine similarity, to figure out the user's *intent*.
4. Keeping a tiny bit of conversation "context" so short follow-up questions
   (e.g. "how much?", "and for refunds?") can still be understood.
5. Returning an appropriate response from the FAQ dataset.

No paid APIs are used — everything here runs locally with open-source
libraries (NLTK + scikit-learn).
"""

import random
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from faq_data import FAQ_DATA


# ---------------------------------------------------------------------------
# 1. Make sure the NLTK data files we need are available.
#    (They only need to be downloaded once; after that NLTK finds them
#    locally, so this is fast on subsequent runs.)
# ---------------------------------------------------------------------------
def _ensure_nltk_data():
    required = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]
    for path, package in required:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except Exception as exc:  # pragma: no cover - network issues, etc.
                print(f"[nlp_engine] Warning: could not download '{package}': {exc}")


_ensure_nltk_data()

# Load stopwords once (e.g. "the", "is", "a", "an"...) and a lemmatizer,
# which reduces words to their base/dictionary form (e.g. "running" -> "run").
try:
    _STOPWORDS = set(stopwords.words("english"))
except LookupError:
    _STOPWORDS = set()

_LEMMATIZER = WordNetLemmatizer()
_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def preprocess_text(text: str):
    """
    Clean and normalize a piece of text, returning a list of tokens.

    Steps:
      1. Lowercase everything      -> "How Much Does It Cost?" -> "how much does it cost?"
      2. Remove punctuation        -> "how much does it cost"
      3. Tokenize (split into words) -> ["how", "much", "does", "it", "cost"]
      4. Remove stop-words          -> ["much", "cost"]   (removes "how", "does", "it")
      5. Lemmatize each token       -> ["much", "cost"]   (already base form here)

    This cleaned token list is what we compare for similarity, so that
    "How much does it cost?" and "what's the cost?" end up looking very
    similar to the model even though they're phrased differently.
    """
    if not text:
        return []

    text = text.lower().translate(_PUNCT_TABLE)

    try:
        tokens = word_tokenize(text)
    except LookupError:
        # Fallback if punkt tokenizer data isn't available for some reason.
        tokens = text.split()

    cleaned_tokens = [
        _LEMMATIZER.lemmatize(tok)
        for tok in tokens
        if tok not in _STOPWORDS and tok.strip() != ""
    ]
    return cleaned_tokens


class ChatbotNLP:
    """
    Wraps the TF-IDF vectorizer and the FAQ dataset, and exposes a single
    `get_response()` method that the Flask app calls for every user message.
    """

    # Similarity thresholds (cosine similarity ranges from 0 to 1).
    # These were picked empirically — feel free to tune them.
    HIGH_CONFIDENCE = 0.35   # confident match -> answer directly
    LOW_CONFIDENCE = 0.15    # weak match -> only used together with context
    CONTEXT_BONUS = 0.12     # bonus added to the previous topic's score

    FALLBACK_RESPONSES = [
        "I'm not totally sure I understood that. Could you rephrase your "
        "question? You can ask me about accounts, services, payments, "
        "refunds, or contact info.",
        "Sorry, I didn't quite catch that. Try asking about things like "
        "'how do I reset my password' or 'what is your refund policy'.",
        "Hmm, I don't have an answer for that yet. Would you like me to "
        "connect you with our contact information instead?",
    ]

    def __init__(self, faq_data=None):
        self.faq_data = faq_data or FAQ_DATA

        # Flatten the FAQ data into two parallel lists:
        #   self._pattern_texts[i]  -> the raw pattern text
        #   self._pattern_tags[i]   -> which intent/tag that pattern belongs to
        self._pattern_texts = []
        self._pattern_tags = []
        self._tag_to_entry = {}

        for entry in self.faq_data:
            tag = entry["tag"]
            self._tag_to_entry[tag] = entry
            for pattern in entry["patterns"]:
                self._pattern_texts.append(pattern)
                self._pattern_tags.append(tag)

        # Build the TF-IDF vectorizer using our custom NLTK-based preprocessor
        # as the tokenizer/analyzer. This is where NLTK and TF-IDF connect:
        # every pattern is first cleaned with preprocess_text(), *then*
        # converted into a numeric vector.
        self._vectorizer = TfidfVectorizer(analyzer=preprocess_text)
        self._pattern_matrix = self._vectorizer.fit_transform(self._pattern_texts)

    def _best_matches_per_tag(self, user_message: str):
        """
        Compute cosine similarity between the user's message and every FAQ
        pattern, then reduce that down to the single best similarity score
        per intent/tag. Returns a dict: {tag: best_score}
        """
        user_vector = self._vectorizer.transform([user_message])
        similarities = cosine_similarity(user_vector, self._pattern_matrix)[0]

        best_per_tag = {}
        for score, tag in zip(similarities, self._pattern_tags):
            if tag not in best_per_tag or score > best_per_tag[tag]:
                best_per_tag[tag] = score
        return best_per_tag

    def get_response(self, user_message: str, last_tag: str = None):
        """
        Main entry point. Given the user's raw message (and optionally the
        tag/topic of the *previous* turn, for basic context handling),
        returns a tuple: (response_text, detected_tag, confidence_score)
        """
        user_message = (user_message or "").strip()
        if not user_message:
            return (
                "It looks like you sent an empty message. Could you type "
                "your question?",
                "empty_input",
                0.0,
            )

        scores = self._best_matches_per_tag(user_message)
        if not scores:
            tag = "fallback"
            confidence = 0.0
        else:
            # Give a small bonus to whatever topic we were just discussing,
            # so short follow-ups like "how much?" lean toward that topic
            # instead of resetting the conversation every time.
            if last_tag and last_tag in scores:
                scores = dict(scores)  # copy so we don't mutate the original
                scores[last_tag] += self.CONTEXT_BONUS

            best_tag = max(scores, key=scores.get)
            best_score = scores[best_tag]

            if best_score >= self.HIGH_CONFIDENCE:
                tag, confidence = best_tag, best_score
            elif best_score >= self.LOW_CONFIDENCE and last_tag:
                # Weak match, but we have context from the previous message —
                # trust it a little more.
                tag, confidence = best_tag, best_score
            else:
                tag, confidence = "fallback", best_score

        if tag == "fallback":
            response = random.choice(self.FALLBACK_RESPONSES)
        else:
            response = random.choice(self._tag_to_entry[tag]["responses"])

        return response, tag, float(confidence)


# A single shared instance the Flask app can import and reuse across requests
# (building the TF-IDF matrix every request would be wasteful).
chatbot_nlp = ChatbotNLP()


if __name__ == "__main__":
    # Quick manual test: run `python nlp_engine.py` to try it from the terminal.
    print("Chatbot NLP engine loaded. Type 'quit' to exit.\n")
    last_tag = None
    while True:
        msg = input("You: ")
        if msg.lower() in ("quit", "exit"):
            break
        reply, tag, conf = chatbot_nlp.get_response(msg, last_tag)
        print(f"Bot ({tag}, confidence={conf:.2f}): {reply}\n")
        last_tag = tag
