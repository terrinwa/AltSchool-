import uuid
import json
from datetime import datetime, timezone

class Expense:
    def __init__(self, title: str, amount: float):
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        self.id = str(uuid.uuid4())  # Unique identifier
        self.title = title
        self.amount = amount
        self.created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.updated_at = self.created_at

    def update(self, title: str = None, amount: float = None):
        if title:
            self.title = title
        if amount is not None:  # Allow amount to be zero
            if amount < 0:
                raise ValueError("Amount must be non-negative")
            self.amount = amount
        self.updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        expense = Expense(data["title"], data["amount"])
        expense.id = data["id"]
        expense.created_at = datetime.fromisoformat(data["created_at"])
        expense.updated_at = datetime.fromisoformat(data["updated_at"])
        return expense


class ExpenseDatabase:
    def __init__(self, file_path="expenses.json"):
        self.file_path = file_path
        self.expenses = []
        self.load_expenses()  # Load data 

    def add_expense(self, expense: Expense, enforce_unique_title=False):
        if enforce_unique_title and any(exp.title.lower() == expense.title.lower() for exp in self.expenses):
            raise ValueError("Expense with this title already exists.")
        self.expenses.append(expense)
        self.save_expenses()

    def remove_expense(self, expense_id: str):
        initial_length = len(self.expenses)
        self.expenses = [expense for expense in self.expenses if expense.id != expense_id]
        self.save_expenses()
        return initial_length != len(self.expenses)  # True if removed, False if not found

    def get_expense_by_id(self, expense_id: str):
        return next((expense for expense in self.expenses if expense.id == expense_id), None)

    def get_expense_by_title(self, expense_title: str):
        return [expense for expense in self.expenses if expense.title.lower() == expense_title.lower()]

    def to_dict(self):
        return [expense.to_dict() for expense in self.expenses]

    def save_expenses(self):
        """ Save expenses to a JSON file """
        with open(self.file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_expenses(self):
        """ Load expenses from a JSON file """
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.expenses = [Expense.from_dict(exp) for exp in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.expenses = []

# Example Usage
if __name__ == "__main__":
    db = ExpenseDatabase()

    # Add an expense
    expense1 = Expense("Groceries", 50.0)
    db.add_expense(expense1)

    # Remove an expense
    removed = db.remove_expense(expense1.id)
    print("Removed:", removed)

    # Save and reload from JSON
    db.save_expenses()
    db.load_expenses()
