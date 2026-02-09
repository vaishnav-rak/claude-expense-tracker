import os
import json
import hashlib
import requests
from datetime import datetime, timedelta

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Cache for tax calculations (24h TTL)
_tax_cache = {}
CACHE_DURATION = timedelta(hours=24)


def _build_prompt(investment_type, amount, deposit_date, withdrawal_date, age_bracket, income_slab):
    holding_days = (datetime.strptime(withdrawal_date, "%Y-%m-%d") - datetime.strptime(deposit_date, "%Y-%m-%d")).days

    return f"""You are an expert Indian tax consultant. Analyze the following investment and calculate the applicable capital gains tax under Indian Income Tax Act.

Investment Details:
- Investment Type: {investment_type}
- Amount Invested: INR {amount:,.2f}
- Date of Investment: {deposit_date}
- Date of Withdrawal: {withdrawal_date}
- Holding Period: {holding_days} days
- Investor Age Bracket: {age_bracket}
- Income Tax Slab: {income_slab}

Respond ONLY with a valid JSON object (no markdown, no explanation outside JSON) with this exact structure:
{{
    "classification": {{
        "investment_category": "string (e.g. Equity Mutual Fund, Debt Mutual Fund, Listed Equity, Gold, Real Estate, Fixed Deposit, etc.)",
        "gain_type": "string (STCG or LTCG)",
        "holding_period_days": {holding_days},
        "ltcg_threshold_days": "number (days required for LTCG classification for this investment type)",
        "holding_analysis": "string (brief explanation of why STCG or LTCG)"
    }},
    "tax_computation": {{
        "applicable_section": "string (e.g. Section 111A, Section 112A, Section 112, etc.)",
        "base_tax_rate_percent": "number",
        "surcharge_percent": "number",
        "cess_percent": "number (typically 4%)",
        "exemption_limit": "number (e.g. 100000 for LTCG on equity under Section 112A)",
        "taxable_amount": "number",
        "tax_before_cess": "number",
        "cess_amount": "number",
        "total_tax": "number",
        "effective_rate_percent": "number"
    }},
    "explanation": {{
        "classification_reasoning": "string (why this investment type was classified this way)",
        "tax_section_reasoning": "string (why this tax section applies)",
        "exemption_details": "string (any exemptions applied and why)",
        "important_notes": "string (any caveats, indexation benefits, grandfathering clauses, etc.)"
    }},
    "confidence": "number between 0 and 1 (your confidence in this analysis)"
}}

Important rules:
- Use the latest Indian tax rules (FY 2024-25 / AY 2025-26)
- For equity mutual funds: STCG if held < 12 months (Section 111A at 15%), LTCG if >= 12 months (Section 112A at 10% above 1L exemption)
- For debt mutual funds: Taxed at income tax slab rate regardless of holding period (post April 2023 rules)
- For listed equity shares: Same as equity mutual funds
- For real estate: STCG if held < 24 months (slab rate), LTCG if >= 24 months (Section 112 at 20% with indexation)
- For gold/gold ETFs: STCG if held < 36 months (slab rate), LTCG if >= 36 months (Section 112 at 20% with indexation)
- Always add 4% Health & Education Cess on tax
- Consider surcharge based on income slab
- Calculate taxable_amount as the gain amount (assume the entire amount is gain for simplicity, unless specified)
"""


def _call_gemini_api(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "topP": 0.8,
            "maxOutputTokens": 2048
        }
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def _parse_gemini_response(response):
    try:
        text = response["candidates"][0]["content"]["parts"][0]["text"]

        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)

        # Validate required keys
        required_keys = ["classification", "tax_computation", "explanation", "confidence"]
        for key in required_keys:
            if key not in result:
                print(f"Missing required key in Gemini response: {key}")
                return None

        return result
    except (KeyError, json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing Gemini response: {e}")
        return None


def _get_cache_key(investment_type, amount, deposit_date, withdrawal_date, age_bracket, income_slab):
    raw = f"{investment_type}|{amount}|{deposit_date}|{withdrawal_date}|{age_bracket}|{income_slab}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_fallback_response(amount, deposit_date, withdrawal_date):
    holding_days = (datetime.strptime(withdrawal_date, "%Y-%m-%d") - datetime.strptime(deposit_date, "%Y-%m-%d")).days
    is_ltcg = holding_days >= 365

    if is_ltcg:
        exemption = min(amount, 100000)
        taxable = max(0, amount - exemption)
        base_rate = 10.0
        tax_before_cess = taxable * base_rate / 100
        cess = tax_before_cess * 0.04
        total_tax = tax_before_cess + cess
    else:
        taxable = amount
        base_rate = 15.0
        tax_before_cess = taxable * base_rate / 100
        cess = tax_before_cess * 0.04
        total_tax = tax_before_cess + cess

    effective_rate = (total_tax / amount * 100) if amount > 0 else 0

    return {
        "classification": {
            "investment_category": "General Investment",
            "gain_type": "LTCG" if is_ltcg else "STCG",
            "holding_period_days": holding_days,
            "ltcg_threshold_days": 365,
            "holding_analysis": f"Holding period of {holding_days} days {'exceeds' if is_ltcg else 'is less than'} the general 365-day threshold for LTCG classification."
        },
        "tax_computation": {
            "applicable_section": "Section 112A (estimated)" if is_ltcg else "Section 111A (estimated)",
            "base_tax_rate_percent": base_rate,
            "surcharge_percent": 0,
            "cess_percent": 4,
            "exemption_limit": 100000 if is_ltcg else 0,
            "taxable_amount": taxable,
            "tax_before_cess": round(tax_before_cess, 2),
            "cess_amount": round(cess, 2),
            "total_tax": round(total_tax, 2),
            "effective_rate_percent": round(effective_rate, 2)
        },
        "explanation": {
            "classification_reasoning": "This is a basic estimate. Without AI analysis, a general 12-month threshold is assumed for LTCG classification.",
            "tax_section_reasoning": f"{'Section 112A is assumed for LTCG on equity-like investments at 10%.' if is_ltcg else 'Section 111A is assumed for STCG on equity-like investments at 15%.'}",
            "exemption_details": f"{'Standard Rs 1,00,000 LTCG exemption applied under Section 112A.' if is_ltcg else 'No exemption applicable for STCG.'}",
            "important_notes": "This is a fallback estimate. For accurate tax computation, please ensure the Gemini API key is configured. Actual tax may vary based on investment type, indexation benefits, and other factors."
        },
        "confidence": 0.3
    }


def calculate_investment_tax(investment_type, amount, deposit_date, withdrawal_date, age_bracket="general", income_slab="above_10l"):
    # Check cache
    cache_key = _get_cache_key(investment_type, amount, deposit_date, withdrawal_date, age_bracket, income_slab)
    now = datetime.now()

    if cache_key in _tax_cache:
        cached = _tax_cache[cache_key]
        if now - cached["timestamp"] < CACHE_DURATION:
            return cached["result"]

    # Build prompt and call Gemini
    prompt = _build_prompt(investment_type, amount, deposit_date, withdrawal_date, age_bracket, income_slab)
    raw_response = _call_gemini_api(prompt)

    if raw_response:
        result = _parse_gemini_response(raw_response)
        if result:
            # Cache the result
            _tax_cache[cache_key] = {"result": result, "timestamp": now}
            return result

    # Fallback if API is unavailable or response is invalid
    fallback = get_fallback_response(amount, deposit_date, withdrawal_date)
    _tax_cache[cache_key] = {"result": fallback, "timestamp": now}
    return fallback
