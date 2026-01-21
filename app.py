import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from collections import defaultdict
from models import db, Expense, Budget

app = Flask(__name__)

# Database configuration
# For local development, use SQLite
# For PythonAnywhere, use MySQL (set DATABASE_URL environment variable)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # PythonAnywhere MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


def get_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return [e.to_dict() for e in expenses]


def get_budgets():
    budgets = Budget.query.all()
    return {b.category: b.amount for b in budgets}


def calculate_totals(expenses):
    totals = defaultdict(float)
    for expense in expenses:
        totals[expense['category']] += expense['amount']
    return dict(totals)


@app.route("/")
def index():
    expenses = get_expenses()
    totals = calculate_totals(expenses)
    budgets = get_budgets()

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
                         expenses=expenses[-10:])


@app.route("/api/budgets", methods=["POST"])
def update_budgets():
    data = request.json
    category = data["category"]
    amount = float(data["budget"])

    budget = Budget.query.filter_by(category=category).first()
    if budget:
        budget.amount = amount
    else:
        budget = Budget(category=category, amount=amount)
        db.session.add(budget)

    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/expense", methods=["POST"])
def add_expense():
    data = request.json
    expense = Expense(
        date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
        category=data["category"],
        amount=float(data["amount"])
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/expenses", methods=["GET"])
def list_expenses():
    expenses = get_expenses()
    return jsonify(expenses)


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False)
