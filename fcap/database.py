"""SQLite storage for conversations and appointments."""

import sqlite3
from typing import List, Optional

from . import config

APPOINTMENT_FIELDS = [
    "id", "patient_name", "patient_email", "appointment_date",
    "appointment_time", "doctor_name", "status", "created_at",
]


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    return sqlite3.connect(db_path or config.DB_PATH)


def init_database(db_path: Optional[str] = None) -> None:
    conn = connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            patient_email TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_conversation(session_id: str, message: str, response: str,
                      db_path: Optional[str] = None) -> None:
    conn = connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, message, response) VALUES (?, ?, ?)",
        (session_id, message, response)
    )
    conn.commit()
    conn.close()


def list_appointments(db_path: Optional[str] = None) -> List[dict]:
    conn = connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(APPOINTMENT_FIELDS, row)) for row in rows]


def create_appointment(patient_name: str, patient_email: str, appointment_date: str,
                       appointment_time: str, doctor_name: str,
                       db_path: Optional[str] = None) -> None:
    conn = connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_name, patient_email, appointment_date, "
        "appointment_time, doctor_name) VALUES (?, ?, ?, ?, ?)",
        (patient_name, patient_email, appointment_date, appointment_time, doctor_name)
    )
    conn.commit()
    conn.close()
