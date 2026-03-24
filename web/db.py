import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    anthropic_api_key TEXT,
                    notion_api_key TEXT,
                    alpha_vantage_api_key TEXT,
                    watchlist_db_id TEXT,
                    research_notes_db_id TEXT,
                    earnings_calendar_db_id TEXT,
                    daily_digest_db_id TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

def get_user_by_email(email):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()

def get_user_by_id(user_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()

def create_user(email, password_hash):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash)
            )
            return cur.fetchone()[0]

def get_all_users():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()

def update_user_keys(user_id, keys: dict):
    allowed = {"anthropic_api_key", "notion_api_key", "alpha_vantage_api_key",
               "watchlist_db_id", "research_notes_db_id", "earnings_calendar_db_id", "daily_digest_db_id"}
    fields = {k: v for k, v in keys.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE users SET {set_clause} WHERE id = %s",
                (*fields.values(), user_id)
            )
