from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from security import (
    decrypt_value,
    encrypt_value,
    hash_password,
    mask_contact,
    mask_name,
    mask_text,
)

DB_PATH = Path("data/hospital.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(seed: bool = True) -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','doctor','receptionist'))
            );

            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                anonymized_name TEXT,
                anonymized_contact TEXT,
                anonymized_diagnosis TEXT,
                date_added TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            """
        )
    if seed:
        seed_users()
        seed_patients()


def seed_users() -> None:
    default_users = [
        ("admin", "admin123", "admin"),
        ("Dr. Bob", "doc123", "doctor"),
        ("Alice_recep", "rec123", "receptionist"),
    ]
    with get_connection() as conn:
        for username, raw_password, role in default_users:
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hash_password(raw_password), role),
            )
        conn.commit()


def seed_patients() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count:
            return
        demo_patients = [
            ("Fatima Khan", "+92-300-1234567", "Hypertension"),
            ("Ahmed Hassan", "+92-321-5678901", "Type 2 Diabetes"),
            ("Zainab Malik", "+92-333-9876543", "Asthma"),
            ("Muhammad Ali", "+92-345-2468135", "Seasonal Allergies"),
            ("Pervaiz Ahmed", "+92-312-3691357", "Migraine"),
        ]
        for name, contact, diagnosis in demo_patients:
            insert_patient(name, contact, diagnosis)


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id, username, password, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if not row:
            return None
        return dict(row)


def insert_patient(name: str, contact: str, diagnosis: str) -> int:
    encrypted_name = encrypt_value(name)
    encrypted_contact = encrypt_value(contact)
    encrypted_diagnosis = encrypt_value(diagnosis)
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO patients (name, contact, diagnosis, date_added)
            VALUES (?, ?, ?, ?)
            """,
            (encrypted_name, encrypted_contact, encrypted_diagnosis, now),
        )
        patient_id = cursor.lastrowid
        conn.execute(
            """
            UPDATE patients
               SET anonymized_name = ?,
                   anonymized_contact = ?,
                   anonymized_diagnosis = ?
             WHERE patient_id = ?
            """,
            (
                mask_name(patient_id),
                mask_contact(contact),
                mask_text(diagnosis),
                patient_id,
            ),
        )
        conn.commit()
        return patient_id


def update_patient(patient_id: int, *, contact: Optional[str] = None, diagnosis: Optional[str] = None) -> None:
    if contact is None and diagnosis is None:
        return
    columns = []
    params: List[Any] = []
    if contact is not None:
        columns.append("contact = ?")
        params.append(encrypt_value(contact))
    if diagnosis is not None:
        columns.append("diagnosis = ?")
        params.append(encrypt_value(diagnosis))
    params.append(patient_id)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE patients SET {', '.join(columns)} WHERE patient_id = ?",
            params,
        )
        row = conn.execute(
            "SELECT contact, diagnosis FROM patients WHERE patient_id = ?",
            (patient_id,),
        ).fetchone()
        if row:
            dec_contact = decrypt_value(row["contact"])
            dec_diag = decrypt_value(row["diagnosis"])
            conn.execute(
                """
                UPDATE patients
                   SET anonymized_contact = ?,
                       anonymized_diagnosis = ?
                 WHERE patient_id = ?
                """,
                (
                    mask_contact(dec_contact),
                    mask_text(dec_diag),
                    patient_id,
                ),
            )
        conn.commit()


def fetch_patients(include_sensitive: bool = False) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM patients ORDER BY datetime(date_added) DESC"
        ).fetchall()
    patients: List[Dict[str, Any]] = []
    for row in rows:
        record: Dict[str, Any] = {
            "patient_id": row["patient_id"],
            "date_added": row["date_added"],
            "anonymized_name": row["anonymized_name"],
            "anonymized_contact": row["anonymized_contact"],
            "anonymized_diagnosis": row["anonymized_diagnosis"],
        }
        if include_sensitive:
            record.update(
                {
                    "name": decrypt_value(row["name"]),
                    "contact": decrypt_value(row["contact"]),
                    "diagnosis": decrypt_value(row["diagnosis"]),
                }
            )
        patients.append(record)
    return patients


def delete_patient(patient_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        conn.commit()


def refresh_anonymized_fields() -> None:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT patient_id, contact, diagnosis FROM patients"
        ).fetchall()
        for row in rows:
            contact = decrypt_value(row["contact"])
            diagnosis = decrypt_value(row["diagnosis"])
            conn.execute(
                """
                UPDATE patients
                   SET anonymized_name = ?,
                       anonymized_contact = ?,
                       anonymized_diagnosis = ?
                 WHERE patient_id = ?
                """,
                (
                    mask_name(row["patient_id"]),
                    mask_contact(contact),
                    mask_text(diagnosis),
                    row["patient_id"],
                ),
            )
        conn.commit()


def log_action(user_id: Optional[int], role: str, action: str, details: str = "") -> None:
    timestamp = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO logs (user_id, role, action, timestamp, details) VALUES (?, ?, ?, ?, ?)",
            (user_id, role, action, timestamp, details[:250]),
        )
        conn.commit()


def fetch_logs(limit: int = 200) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY datetime(timestamp) DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_log_counts_by_day(days: int = 14) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT substr(timestamp, 1, 10) AS day, COUNT(*) AS total
              FROM logs
             WHERE timestamp >= datetime('now', ?)
             GROUP BY day
             ORDER BY day
            """,
            (f"-{days} days",),
        ).fetchall()
    return [dict(row) for row in rows]


def patient_count() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM patients").fetchone()
        return int(row["total"]) if row else 0
