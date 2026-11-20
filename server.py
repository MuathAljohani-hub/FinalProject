import sqlite3
from flask import Flask, request

DB_NAME = "iftar.db"
CATEGORIES = ["Main", "Soup", "Dessert", "Drink", "Appetizer"]


# ---------- Part 1: the database ----------

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS dishes ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name TEXT NOT NULL, "
                    "category TEXT NOT NULL, "
                    "cost REAL NOT NULL)"
                )
        finally:
            conn.close()

    def add_dish(self, name, category, cost):
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                cur = conn.execute(
                    "INSERT INTO dishes (name, category, cost) VALUES (?, ?, ?)",
                    (name, category, cost),
                )
            return cur.lastrowid
        finally:
            conn.close()

    def get_all(self):
        conn = sqlite3.connect(self.db_name)
        try:
            rows = conn.execute(
                "SELECT id, name, category, cost FROM dishes ORDER BY id"
            ).fetchall()
            return rows
        finally:
            conn.close()

    def update_dish(self, dish_id, name, category, cost):
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                cur = conn.execute(
                    "UPDATE dishes SET name = ?, category = ?, cost = ? WHERE id = ?",
                    (name, category, cost, dish_id),
                )
            return cur.rowcount > 0
        finally:
            conn.close()

    def delete_dish(self, dish_id):
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                cur = conn.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            return cur.rowcount > 0
        finally:
            conn.close()

    def get_total(self):
        total = 0
        for id, name, category, cost in self.get_all():
            total = total + cost
        return total


# ---------- Part 2: Flask ----------

db = Database(DB_NAME)
app = Flask(__name__)


def check_input(name, category, cost_text):
    # returns an error message, or None when the input is fine
    if name == "":
        return "Name is required"
    if category not in CATEGORIES:
        return "Category must be Main, Soup, Dessert, Drink or Appetizer"
    try:
        cost = float(cost_text)
    except ValueError:
        return "Cost must be a number"
    if cost < 0:
        return "Cost cannot be negative"
    return None


@app.route("/dishes")
def list_dishes():
    dishes = []
    for id, name, category, cost in db.get_all():
        dishes.append({"id": id, "name": name, "category": category, "cost": cost})
    return {"dishes": dishes}          # a dict: Flask sends it as JSON


@app.route("/dishes/total")
def total():
    return {"total": db.get_total()}


@app.route("/dishes/add", methods=["POST"])
def add_dish():
    name = request.form["name"].strip()
    category = request.form["category"]
    cost_text = request.form["cost"]

    error = check_input(name, category, cost_text)
    if error:
        return {"error": error}, 400

    new_id = db.add_dish(name, category, float(cost_text))
    return {"message": "Dish added", "id": new_id}


@app.route("/dishes/edit", methods=["POST"])
def edit_dish():
    try:
        dish_id = int(request.form["id"])
    except ValueError:
        return {"error": "id must be a whole number"}, 400

    name = request.form["name"].strip()
    category = request.form["category"]
    cost_text = request.form["cost"]

    error = check_input(name, category, cost_text)
    if error:
        return {"error": error}, 400

    found = db.update_dish(dish_id, name, category, float(cost_text))
    if not found:
        return {"error": "Dish not found"}, 404
    return {"message": "Dish updated"}


@app.route("/dishes/delete", methods=["POST"])
def delete_dish():
    try:
        dish_id = int(request.form["id"])
    except ValueError:
        return {"error": "id must be a whole number"}, 400

    found = db.delete_dish(dish_id)
    if not found:
        return {"error": "Dish not found"}, 404
    return {"message": "Dish deleted"}


if __name__ == "__main__":
    app.run(port=5050)