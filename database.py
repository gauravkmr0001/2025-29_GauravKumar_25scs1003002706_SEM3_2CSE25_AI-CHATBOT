"""
database.py
------------
Handles everything related to storing chat history in an SQLite database.

SQLite is a lightweight, file-based database that needs no separate server —
perfect for a small/medium project like this chatbot. The database file
(chatbot.db) will be created automatically the first time the app runs.

Table schema: conversations
    id            INTEGER  primary key, auto-incremented
    user_message  TEXT     the message typed by the user
    bot_response  TEXT     the chatbot's reply
    intent        TEXT     the detected intent/category (e.g. "greeting")
    timestamp     TEXT     when the message was logged (ISO format)
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file (stored in the same folder as this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.db")


def get_connection():
    """Create and return a new SQLite connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Create the 'conversations' table if it doesn't already exist.
    Safe to call every time the app starts up.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            intent TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    print(f"[database] Database ready at: {DB_PATH}")


def log_conversation(user_message: str, bot_response: str, intent: str = None):
    """
    Insert a new row recording one exchange between the user and the bot.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO conversations (user_message, bot_response, intent, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (user_message, bot_response, intent, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def get_recent_conversations(limit: int = 50):
    """
    Return the most recent `limit` conversation rows, newest first.
    Useful for an admin view or debugging.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_message, bot_response, intent, timestamp
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    # Allow running `python database.py` directly to just initialize the DB.
    init_db()
