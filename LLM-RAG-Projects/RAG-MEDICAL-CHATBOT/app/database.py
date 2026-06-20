import os
import sqlite3
import threading
from typing import List

from app.schema import Message


class ChatHistoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._initialize()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
                ON chat_messages(session_id, created_at, id)
                """
            )
            conn.commit()

    def get_messages(self, session_id: str) -> List[Message]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            ).fetchall()

        return [
            Message(role=row["role"], content=row["content"])
            for row in rows
        ]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO chat_messages(session_id, role, content)
                    VALUES(?, ?, ?)
                    """,
                    (session_id, role, content),
                )
                conn.commit()

    def clear_messages(self, session_id: str) -> None:
        with self._lock:
            with self._connection() as conn:
                conn.execute(
                    "DELETE FROM chat_messages WHERE session_id = ?",
                    (session_id,),
                )
                conn.commit()
