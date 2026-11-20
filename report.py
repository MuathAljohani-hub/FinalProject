import json
import threading
from urllib.request import urlopen

URL = "http://127.0.0.1:5050/dishes"
REPORT_FILE = "report.txt"


def get_dishes():
    # asks the Flask server for all the dishes (the answer is JSON)
    with urlopen(URL, timeout=5) as response:
        text = response.read().decode()
    data = json.loads(text)
    return data["dishes"]


def write_report(dishes, outcome):
    # this function runs inside the thread: it writes the text file
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as fhand:
            fhand.write("Iftar menu report\n")
            fhand.write("-----------------\n")
            total = 0
            for dish in dishes:
                fhand.write(str(dish["id"]) + ". " + dish["name"]
                            + " (" + dish["category"] + ") - "
                            + str(dish["cost"]) + "\n")
                total = total + dish["cost"]
            if len(dishes) == 0:
                fhand.write("No dishes yet\n")
            fhand.write("-----------------\n")
            fhand.write("Total: " + str(round(total, 2)) + "\n")
        outcome.append("saved")
    except OSError as error:
        outcome.append("not saved: " + str(error))


def main():
    # step 1: get the records from the server
    try:
        dishes = get_dishes()
    except OSError:
        # no server, a timeout and an HTTP error are all kinds of OSError
        print("Cannot get the dishes. Is server.py running?")
        return

    # step 2: one thread writes the file
    outcome = []
    t = threading.Thread(target=write_report, args=(dishes, outcome))
    t.start()

    # step 3: wait for the thread, then say what happened
    t.join()
    if outcome[0] == "saved":
        print("Report saved in " + REPORT_FILE)
    else:
        print("Report " + outcome[0])


if __name__ == "__main__":
    main()