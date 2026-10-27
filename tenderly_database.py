import sqlite3
import pandas as pd
from tenderly_settings import DB_NAME, hash_password


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenderly_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            organization TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenderly_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tender_name TEXT,
            eligibility_score REAL,
            verdict TEXT,
            clauses_checked INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES tenderly_users(id)
        )
    """)

    connection.commit()
    connection.close()


def register_user(full_name, email, organization, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM tenderly_users WHERE email = ?", (email,))
    if cursor.fetchone():
        connection.close()
        return False, "An account with this email already exists."

    cursor.execute(
        "INSERT INTO tenderly_users (full_name, email, organization, password_hash) VALUES (?, ?, ?, ?)",
        (full_name, email, organization, hash_password(password))
    )

    connection.commit()
    connection.close()
    return True, "Account created successfully."


def login_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, full_name, email, organization FROM tenderly_users WHERE email = ? AND password_hash = ?",
        (email, hash_password(password))
    )

    user = cursor.fetchone()
    connection.close()

    if user:
        return {
            "id": user[0],
            "full_name": user[1],
            "email": user[2],
            "organization": user[3]
        }

    return None


def save_check(user_id, tender_name, eligibility_score, verdict, clauses_checked):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tenderly_checks (user_id, tender_name, eligibility_score, verdict, clauses_checked) VALUES (?, ?, ?, ?, ?)",
        (user_id, tender_name, eligibility_score, verdict, clauses_checked)
    )

    connection.commit()
    connection.close()


def get_user_checks(user_id):
    connection = get_connection()
    df = pd.read_sql_query(
        "SELECT id, tender_name, eligibility_score, verdict, clauses_checked, created_at FROM tenderly_checks WHERE user_id = ? ORDER BY created_at DESC",
        connection,
        params=(user_id,)
    )
    connection.close()
    return df


def get_user_statistics(user_id):
    df = get_user_checks(user_id)

    if df.empty:
        return {
            "total_checks": 0,
            "eligible": 0,
            "not_eligible": 0,
            "partial": 0,
            "average_score": 0
        }

    return {
        "total_checks": len(df),
        "eligible": len(df[df["verdict"] == "Eligible"]),
        "not_eligible": len(df[df["verdict"] == "Not Eligible"]),
        "partial": len(df[df["verdict"] == "Partially Eligible"]),
        "average_score": df["eligibility_score"].mean()
    }
