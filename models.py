import json
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


class TaxCalculation(db.Model):
    __tablename__ = 'tax_calculations'

    id = db.Column(db.Integer, primary_key=True)
    investment_type = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    deposit_date = db.Column(db.Date, nullable=False)
    withdrawal_date = db.Column(db.Date, nullable=False)
    age_bracket = db.Column(db.String(50), nullable=False)
    income_slab = db.Column(db.String(50), nullable=False)
    ai_report = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0)
    gain_type = db.Column(db.String(10), nullable=False)
    total_tax = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            report = json.loads(self.ai_report)
        except (json.JSONDecodeError, TypeError):
            report = {}
        return {
            'id': self.id,
            'investment_type': self.investment_type,
            'amount': self.amount,
            'deposit_date': self.deposit_date.strftime('%Y-%m-%d'),
            'withdrawal_date': self.withdrawal_date.strftime('%Y-%m-%d'),
            'age_bracket': self.age_bracket,
            'income_slab': self.income_slab,
            'ai_report': report,
            'confidence': self.confidence,
            'gain_type': self.gain_type,
            'total_tax': self.total_tax,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
