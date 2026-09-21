import sqlite3
import os

class Database:
    def __init__(self, db_path="gamedata.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._setup()

    def _setup(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS attributes (
                    entity_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE,
                    PRIMARY KEY(entity_id, key)
                )
            """)
            # Enable SQLite foreign key constraint enforcement
            self.conn.execute("PRAGMA foreign_keys = ON;")

    def execute(self, sql, params=()):
        with self.conn:
            return self.conn.execute(sql, params)

    def query(self, sql, params=()):
        return self.conn.execute(sql, params).fetchall()

    def query_one(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()
