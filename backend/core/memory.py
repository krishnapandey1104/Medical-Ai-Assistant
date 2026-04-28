import sqlite3
import bcrypt
from datetime import datetime, timezone, timedelta

DB_PATH = "chat_memory.db"


# =========================================================
# DB CONNECTION
# =========================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")

    return conn


# =========================================================
# INIT DB (WITH MIGRATION FIX)
# =========================================================
def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        # USERS
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                password BLOB
            )
        """)

        # DEFAULT USER
        c.execute("SELECT id FROM users WHERE id='user1'")
        if not c.fetchone():
            hashed = bcrypt.hashpw("test".encode(), bcrypt.gensalt())
            c.execute(
                "INSERT INTO users (id, password) VALUES (?, ?)",
                ("user1", hashed)
            )

        # SESSIONS (WITH created_at)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                title TEXT,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        # SAFE MIGRATION (if old DB exists)
        try:
            c.execute("ALTER TABLE sessions ADD COLUMN created_at TEXT")
        except:
            pass

        # MESSAGES
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)

        # REPORTS
        c.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                report_text TEXT,
                created_at TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)

        # INDEXES
        c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_reports_session ON reports(session_id)")

        conn.commit()


# =========================================================
# AUTH
# =========================================================
def create_user(user_id, password):
    with get_conn() as conn:
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            conn.execute(
                "INSERT INTO users (id, password) VALUES (?, ?)",
                (user_id, hashed)
            )
            conn.commit()
            return True
        except Exception as e:
            print("USER CREATE ERROR:", e)
            return False


def authenticate_user(user_id, password):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT password FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

        if row:
            return bcrypt.checkpw(password.encode(), row["password"])

    return False


# =========================================================
# SESSION HELPERS
# =========================================================
def validate_session(session_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM sessions WHERE id=?",
            (session_id,)
        ).fetchone()

        if not row:
            raise Exception("Invalid session ID")


def create_session(user_id="user1", title="New Chat"):
    with get_conn() as conn:

        # ensure user exists
        row = conn.execute(
            "SELECT id FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

        if not row:
            create_user(user_id, "test")

        cursor = conn.execute(
            "INSERT INTO sessions (user_id, title, created_at) VALUES (?, ?, ?)",
            (user_id, title, datetime.now(timezone.utc).isoformat())
        )

        conn.commit()
        return cursor.lastrowid


def get_sessions(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title FROM sessions WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()

        return [{"id": r["id"], "title": r["title"]} for r in rows]


def get_recent_sessions(user_id):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, title FROM sessions
            WHERE user_id=? AND created_at >= ?
            ORDER BY id DESC
        """, (user_id, cutoff)).fetchall()

        return [{"id": r["id"], "title": r["title"]} for r in rows]


def rename_session(session_id, new_title):
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET title=? WHERE id=?",
            (new_title, session_id)
        )
        conn.commit()


def delete_session(session_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM reports WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        conn.commit()


# =========================================================
# MESSAGES
# =========================================================
def add_message(session_id, role, content):
    with get_conn() as conn:

        # validate session
        row = conn.execute(
            "SELECT id FROM sessions WHERE id=?",
            (session_id,)
        ).fetchone()

        if not row:
            print("❌ Invalid session_id:", session_id)
            return

        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now(timezone.utc).isoformat())
        )

        # AUTO TITLE (first user message)
        if role == "user":
            count = conn.execute(
                "SELECT COUNT(*) as c FROM messages WHERE session_id=?",
                (session_id,)
            ).fetchone()["c"]

            if count == 1:
                title = content[:30]
                conn.execute(
                    "UPDATE sessions SET title=? WHERE id=?",
                    (title, session_id)
                )

        conn.commit()


def get_messages(session_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id",
            (session_id,)
        ).fetchall()

        return [{"role": r["role"], "content": r["content"]} for r in rows]


# =========================================================
# REPORTS
# =========================================================
def save_report(session_id, report_text):
    with get_conn() as conn:

        row = conn.execute(
            "SELECT id FROM sessions WHERE id=?",
            (session_id,)
        ).fetchone()

        if not row:
            print("❌ Invalid session for report:", session_id)
            return

        report_text = report_text[:4000]

        conn.execute(
            "INSERT INTO reports (session_id, report_text, created_at) VALUES (?, ?, ?)",
            (session_id, report_text, datetime.now(timezone.utc).isoformat())
        )

        conn.commit()


def get_latest_report(session_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT report_text FROM reports WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,)
        ).fetchone()

        return row["report_text"] if row else ""