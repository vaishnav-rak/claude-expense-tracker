from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Supported currencies
SUPPORTED_CURRENCIES = ['INR', 'USD', 'GBP', 'THB']
DEFAULT_CURRENCY = 'INR'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in INR (converted)
    original_amount = db.Column(db.Float, nullable=False, default=0)  # Original amount in original currency
    original_currency = db.Column(db.String(3), nullable=False, default='INR')  # Original currency code
    exchange_rate = db.Column(db.Float, nullable=False, default=1.0)  # Rate used for conversion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'category': self.category,
            'amount': self.amount,  # INR value
            'original_amount': self.original_amount,
            'original_currency': self.original_currency,
            'exchange_rate': self.exchange_rate
        }


class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount
        }
