import json
import socket
import tkinter as tk
from tkinter import messagebox
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

BASE_URL = "http://127.0.0.1:5050"


def send_request(path, fields=None):
    """Asks the server. Returns (data, error_message): one of them is None."""
    url = BASE_URL + path
    data = None
    if fields is not None:
        # fields given: this is a POST, and the body must be bytes
        data = urlencode(fields).encode()

    try:
        with urlopen(url, data=data, timeout=5) as response:
            text = response.read().decode()
            return json.loads(text), None
    except HTTPError as error:
        # the server answered 400 or 404, and its body holds the message
        try:
            body = json.loads(error.read().decode())
            return None, body["error"]
        except ValueError:
            return None, "Server error " + str(error.code)
    except socket.timeout:
        return None, "The server took too long to answer"
    except URLError:
        return None, "Cannot reach the server. Is server.py running?"


class DishWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Iftar Menu Planner")
        self.geometry("520x560")

        # the text boxes
        tk.Label(self, text="ID (for edit and delete)").grid(row=0, column=0, padx=10, pady=5)
        self.id_box = tk.Entry(self)
        self.id_box.grid(row=0, column=1)

        tk.Label(self, text="Name").grid(row=1, column=0, padx=10, pady=5)
        self.name_box = tk.Entry(self)
        self.name_box.grid(row=1, column=1)

        tk.Label(self, text="Category").grid(row=2, column=0, padx=10, pady=5)
        self.category_box = tk.Entry(self)
        self.category_box.grid(row=2, column=1)

        tk.Label(self, text="Main, Soup, Dessert, Drink or Appetizer").grid(row=3, column=1)

        tk.Label(self, text="Cost").grid(row=4, column=0, padx=10, pady=5)
        self.cost_box = tk.Entry(self)
        self.cost_box.grid(row=4, column=1)

        # the buttons
        tk.Button(self, text="Add", command=self.add).grid(row=5, column=0, pady=10)
        tk.Button(self, text="Edit", command=self.edit).grid(row=5, column=1)
        tk.Button(self, text="Delete", command=self.delete).grid(row=5, column=2)
        tk.Button(self, text="Refresh", command=self.refresh).grid(row=5, column=3)

        # the message label: success or error
        self.message_label = tk.Label(self, text="Welcome")
        self.message_label.grid(row=6, column=0, columnspan=4, pady=5)

        # the list of dishes and the total
        self.list_label = tk.Label(self, text="")
        self.list_label.grid(row=7, column=0, columnspan=4, pady=5)

        self.total_label = tk.Label(self, text="Total: 0")
        self.total_label.grid(row=8, column=0, columnspan=4, pady=5)

        self.refresh()

    # ---- small helpers ----

    def show_ok(self, text):
        self.message_label.config(text="Success: " + text)

    def show_error(self, text):
        self.message_label.config(text="Error: " + text)

    def read_id(self, title):
        # returns the id as a whole number, or None after a warning
        try:
            return int(self.id_box.get())
        except ValueError:
            messagebox.showwarning(title, "Type the dish ID as a whole number")
            return None

    def read_fields(self):
        return {
            "name": self.name_box.get(),
            "category": self.category_box.get(),
            "cost": self.cost_box.get(),
        }

    # ---- the methods that the buttons call ----

    def refresh(self):
        data, error = send_request("/dishes")
        if error:
            self.show_error(error)
            return

        text = ""
        for dish in data["dishes"]:
            text = (text + str(dish["id"]) + ". " + dish["name"]
                    + " (" + dish["category"] + ") - " + str(dish["cost"]) + "\n")
        if text == "":
            text = "No dishes yet"
        self.list_label.config(text=text)

        data, error = send_request("/dishes/total")
        if error:
            self.show_error(error)
            return
        self.total_label.config(text="Total: " + str(round(data["total"], 2)))

    def add(self):
        data, error = send_request("/dishes/add", self.read_fields())
        if error:
            self.show_error(error)
            return
        self.show_ok(data["message"])
        self.refresh()

    def edit(self):
        dish_id = self.read_id("Edit")
        if dish_id is None:
            return
        fields = self.read_fields()
        fields["id"] = dish_id
        data, error = send_request("/dishes/edit", fields)
        if error:
            self.show_error(error)
            return
        self.show_ok(data["message"])
        self.refresh()

    def delete(self):
        dish_id = self.read_id("Delete")
        if dish_id is None:
            return
        sure = messagebox.askyesno("Delete", "Delete dish " + str(dish_id) + "?")
        if not sure:
            return
        data, error = send_request("/dishes/delete", {"id": dish_id})
        if error:
            self.show_error(error)
            return
        self.show_ok(data["message"])
        self.refresh()


if __name__ == "__main__":
    window = DishWindow()
    window.mainloop()