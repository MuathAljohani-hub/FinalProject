import sqlite3
from flask import Flask, request, jsonify

DB_NAME = "iftar.db"


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.get_connection()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    cost REAL NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


db = Database(DB_NAME)
app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=5050)