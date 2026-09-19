"""
init_db.py
----------
Small standalone script to (re)initialize the SQLite database.

Usually you don't need to run this manually — app.py calls init_db()
automatically on startup. But it's handy to have as a separate script,
e.g. if you want to set up the database before first run, or reset it
in development.

Usage:
    python init_db.py
"""

from database import init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully. You can now run 'python app.py'.")
