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

    def add_dish(self, name, category, cost):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO dishes (name, category, cost) VALUES (?, ?, ?)",
                    (name, category, cost),
                )
            return cursor.lastrowid
        finally:
            conn.close()

    def get_all(self):
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM dishes ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_dish(self, dish_id, name, category, cost):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "UPDATE dishes SET name = ?, category = ?, cost = ? WHERE id = ?",
                    (name, category, cost, dish_id),
                )
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_dish(self, dish_id):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM dishes WHERE id = ?",
                    (dish_id,),
                )
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_total(self):
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) AS total FROM dishes"
            )
            return cursor.fetchone()["total"]
        finally:
            conn.close()


db = Database(DB_NAME)
app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=5050)