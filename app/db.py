import time
import psycopg
from psycopg.rows import dict_row
from app.core.config import settings

def get_db_connection():
    # Tentative de connexion avec retry pour attendre que le DNS/DB soit prêt
    retries = 5
    while retries > 0:
        try:
            return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)
        except psycopg.OperationalError as e:
            retries -= 1
            if retries == 0:
                raise e
            time.sleep(2)

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    activation_code TEXT,
                    code_expires_at DOUBLE PRECISION,
                    is_active BOOLEAN DEFAULT FALSE
                );
            """)
            conn.commit()
