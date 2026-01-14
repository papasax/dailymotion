from app.db import get_db_connection

class UserRepo:
    @staticmethod
    def create(email: str, password_hash: str, code: str, expires_at: float):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email, password_hash, activation_code, code_expires_at) VALUES (%s, %s, %s, %s)",
                    (email, password_hash, code, expires_at)
                )

    @staticmethod
    def get_by_email(email: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cur.fetchone()

    @staticmethod
    def set_active(email: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET is_active = TRUE WHERE email = %s", (email,))
