import sqlite3
from flask import Flask, request, jsonify

DB_NAME = "iftar.db"
CATEGORIES = ["Main", "Soup", "Dessert", "Drink", "Appetizer"]


# ---------- Part 1: the database ----------

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        # a new connection for every request
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row   # rows can be turned into dictionaries
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
            with conn:   # saves the change (commit)
                cursor = conn.execute(
                    "INSERT INTO dishes (name, category, cost) VALUES (?, ?, ?)",
                    (name, category, cost),
                )
            return cursor.lastrowid   # the id of the new dish
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
            return cursor.rowcount > 0   # False if the id does not exist
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
            return cursor.rowcount > 0   # False if the id does not exist
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


# ---------- Part 2: Flask ----------

db = Database(DB_NAME)
app = Flask(__name__)


def check_input(name, category, cost_text):
    """Returns an error message, or None if everything is fine."""
    if name == "":
        return "Name is required"
    if category not in CATEGORIES:
        return "Category must be one of: " + ", ".join(CATEGORIES)
    try:
        cost = float(cost_text)
    except ValueError:
        return "Cost must be a number"
    if cost < 0:
        return "Cost cannot be negative"
    return None


@app.route("/dishes", methods=["GET"])
def list_dishes():
    return jsonify(db.get_all())


@app.route("/dishes/total", methods=["GET"])
def total():
    return jsonify({"total": db.get_total()})


@app.route("/dishes/add", methods=["POST"])
def add_dish():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    cost_text = request.form.get("cost", "").strip()

    error = check_input(name, category, cost_text)
    if error:
        return jsonify({"error": error}), 400

    new_id = db.add_dish(name, category, float(cost_text))
    return jsonify({"message": "Dish added", "id": new_id})


@app.route("/dishes/edit", methods=["POST"])
def edit_dish():
    try:
        dish_id = int(request.form.get("id", ""))
    except ValueError:
        return jsonify({"error": "id must be a whole number"}), 400

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    cost_text = request.form.get("cost", "").strip()

    error = check_input(name, category, cost_text)
    if error:
        return jsonify({"error": error}), 400

    found = db.update_dish(dish_id, name, category, float(cost_text))
    if not found:
        return jsonify({"error": "Dish not found"}), 404
    return jsonify({"message": "Dish updated"})


@app.route("/dishes/delete", methods=["POST"])
def delete_dish():
    try:
        dish_id = int(request.form.get("id", ""))
    except ValueError:
        return jsonify({"error": "id must be a whole number"}), 400

    found = db.delete_dish(dish_id)
    if not found:
        return jsonify({"error": "Dish not found"}), 404
    return jsonify({"message": "Dish deleted"})


if __name__ == "__main__":
    app.run(port=5050)