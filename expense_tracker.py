import csv
import json
from collections import defaultdict

BUDGETS_FILE = "budgets.json"


def load_expenses(filename="expenses.csv"):
    """Load expenses from a CSV file."""
    expenses = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            expenses.append({
                "date": row["Date"],
                "category": row["Category"],
                "amount": float(row["Amount"])
            })
    return expenses


def calculate_totals_by_category(expenses):
    """Calculate total spending per category."""
    totals = defaultdict(float)
    for expense in expenses:
        totals[expense["category"]] += expense["amount"]
    return dict(totals)


def load_budgets():
    """Load budgets from JSON file."""
    try:
        with open(BUDGETS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_budgets(budgets):
    """Save budgets to JSON file."""
    with open(BUDGETS_FILE, "w") as file:
        json.dump(budgets, file, indent=2)
    print(f"\nBudgets saved to {BUDGETS_FILE}")


def get_budgets(categories):
    """Prompt user to set budgets for each category."""
    existing_budgets = load_budgets()

    if existing_budgets:
        print("\n=== Existing Budgets Found ===")
        for cat, amount in sorted(existing_budgets.items()):
            print(f"  {cat}: ${amount:.2f}")
        choice = input("\nUse existing budgets? (y/n): ").strip().lower()
        if choice == "y":
            return existing_budgets

    print("\n=== Set Budgets ===")
    print("(Press Enter to skip a category)\n")
    budgets = {}
    for category in sorted(categories):
        default = existing_budgets.get(category)
        prompt = f"Budget for {category}"
        if default:
            prompt += f" [{default}]"
        prompt += ": $"

        while True:
            user_input = input(prompt)
            if user_input.strip() == "":
                if default:
                    budgets[category] = default
                break
            try:
                budgets[category] = float(user_input)
                break
            except ValueError:
                print("Please enter a valid number.")

    if budgets:
        save_budgets(budgets)

    return budgets


def display_totals(totals, budgets=None):
    """Display spending totals by category with budget alerts."""
    print("\n=== Spending by Category ===\n")
    grand_total = 0
    alerts = []

    for category, amount in sorted(totals.items()):
        budget_info = ""
        if budgets and category in budgets:
            budget = budgets[category]
            remaining = budget - amount
            if amount > budget:
                budget_info = f" [OVER BUDGET by ${amount - budget:.2f}]"
                alerts.append((category, amount, budget))
            else:
                budget_info = f" [${remaining:.2f} remaining of ${budget:.2f}]"
        print(f"{category}: ${amount:.2f}{budget_info}")
        grand_total += amount

    print(f"\n{'Total':-<20} ${grand_total:.2f}")

    if alerts:
        print("\n⚠️  BUDGET ALERTS ⚠️")
        for category, spent, budget in alerts:
            print(f"  • {category}: Spent ${spent:.2f} / Budget ${budget:.2f}")


def main():
    try:
        expenses = load_expenses()
        totals = calculate_totals_by_category(expenses)

        categories = set(totals.keys())
        budgets = get_budgets(categories)

        display_totals(totals, budgets)
    except FileNotFoundError:
        print("Error: expenses.csv not found. Please create the file first.")
    except KeyError as e:
        print(f"Error: Missing column {e} in CSV file.")


if __name__ == "__main__":
    main()
