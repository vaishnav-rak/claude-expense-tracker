from flask import Flask, render_template, request, jsonify
import csv
import json
from collections import defaultdict

app = Flask(__name__)
BUDGETS_FILE = "budgets.json"
EXPENSES_FILE = "expenses.csv"


def load_expenses():
    expenses = []
    try:
        with open(EXPENSES_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                expenses.append({
                    "date": row["Date"],
                    "category": row["Category"],
                    "amount": float(row["Amount"])
                })
    except FileNotFoundError:
        pass
    return expenses


def load_budgets():
    try:
        with open(BUDGETS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_budgets(budgets):
    with open(BUDGETS_FILE, "w") as file:
        json.dump(budgets, file, indent=2)


def calculate_totals(expenses):
    totals = defaultdict(float)
    for expense in expenses:
        totals[expense["category"]] += expense["amount"]
    return dict(totals)


@app.route("/")
def index():
    expenses = load_expenses()
    totals = calculate_totals(expenses)
    budgets = load_budgets()

    categories_data = []
    for category, spent in sorted(totals.items()):
        budget = budgets.get(category, 0)
        percentage = (spent / budget * 100) if budget > 0 else 0
        over_budget = spent > budget if budget > 0 else False
        categories_data.append({
            "name": category,
            "spent": spent,
            "budget": budget,
            "percentage": min(percentage, 100),
            "over_budget": over_budget,
            "over_amount": spent - budget if over_budget else 0
        })

    grand_total = sum(totals.values())
    total_budget = sum(budgets.values())

    return render_template("index.html",
                         categories=categories_data,
                         grand_total=grand_total,
                         total_budget=total_budget,
                         expenses=expenses[-10:])  # Last 10 expenses


@app.route("/api/budgets", methods=["POST"])
def update_budgets():
    data = request.json
    budgets = load_budgets()
    budgets[data["category"]] = float(data["budget"])
    save_budgets(budgets)
    return jsonify({"success": True})


@app.route("/api/expense", methods=["POST"])
def add_expense():
    data = request.json
    with open(EXPENSES_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data["date"], data["category"], data["amount"]])
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
