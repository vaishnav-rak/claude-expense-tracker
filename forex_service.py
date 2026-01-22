import requests
from datetime import datetime, timedelta
from functools import lru_cache

# Using ExchangeRate-API (free tier - no API key required for basic usage)
# Alternative: Open Exchange Rates, Fixer.io, etc.
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/INR"

# Cache for exchange rates (refreshed every hour)
_rates_cache = {
    'rates': None,
    'last_updated': None
}

CACHE_DURATION = timedelta(hours=1)


def get_exchange_rates():
    """
    Fetch live exchange rates with INR as base currency.
    Returns rates as: 1 INR = X foreign currency
    We need the inverse for conversion (1 foreign = X INR)
    """
    now = datetime.now()

    # Return cached rates if still valid
    if (_rates_cache['rates'] is not None and
        _rates_cache['last_updated'] is not None and
        now - _rates_cache['last_updated'] < CACHE_DURATION):
        return _rates_cache['rates']

    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # API returns: 1 INR = X other currency
        # We need: 1 other currency = X INR (inverse)
        api_rates = data.get('rates', {})

        # Calculate inverse rates (how much INR for 1 unit of foreign currency)
        rates = {'INR': 1.0}
        for currency in ['USD', 'GBP', 'THB']:
            if currency in api_rates and api_rates[currency] > 0:
                rates[currency] = 1 / api_rates[currency]

        _rates_cache['rates'] = rates
        _rates_cache['last_updated'] = now

        return rates

    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        # Return fallback rates if API fails
        return get_fallback_rates()


def get_fallback_rates():
    """
    Fallback rates if API is unavailable.
    These are approximate rates and should be updated periodically.
    Values represent: 1 unit of currency = X INR
    """
    return {
        'INR': 1.0,
        'USD': 83.0,    # 1 USD = ~83 INR
        'GBP': 105.0,   # 1 GBP = ~105 INR
        'THB': 2.4      # 1 THB = ~2.4 INR
    }


def convert_to_inr(amount, currency):
    """
    Convert an amount from a foreign currency to INR.

    Args:
        amount: The amount in the original currency
        currency: The currency code (INR, USD, GBP, THB)

    Returns:
        tuple: (amount_in_inr, exchange_rate_used)
    """
    if currency == 'INR':
        return amount, 1.0

    rates = get_exchange_rates()
    rate = rates.get(currency, get_fallback_rates().get(currency, 1.0))

    amount_in_inr = amount * rate
    return round(amount_in_inr, 2), rate


def get_currency_symbol(currency):
    """Get the symbol for a currency code."""
    symbols = {
        'INR': '₹',
        'USD': '$',
        'GBP': '£',
        'THB': '฿'
    }
    return symbols.get(currency, currency)


def format_currency(amount, currency):
    """Format an amount with its currency symbol."""
    symbol = get_currency_symbol(currency)
    return f"{symbol}{amount:.2f}"
