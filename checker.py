from decimal import Decimal, InvalidOperation

APPROVED = "Approved"
REJECTED = "Rejected"
MANUAL = "Needs Manual Sign-off"

VALID_ACTIONS = {"buy": "Buy", "sell": "Sell"}


def to_decimal(value):
    """Convert to Decimal, or return None if not a finite number."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    return d if d.is_finite() else None


def _result(decision, reason):
    return {"decision": decision, "reason": reason}


def check_trade(trade, portfolios):
    # validate 
    qty = to_decimal(trade.get("quantity"))
    price = to_decimal(trade.get("price"))
    action = VALID_ACTIONS.get(str(trade.get("action", "")).strip().lower())

    if qty is None or price is None or qty <= 0 or price <= 0 or action is None:
        return _result(REJECTED, "Invalid trade data.")

    #  unknown portfolio can't be checked.
    portfolio = portfolios.get(trade.get("portfolio_id"))
    if portfolio is None:
        return _result(REJECTED, "Unknown portfolio.")

    security_id = trade.get("security_id")
    cash = to_decimal(portfolio["cash_balance"])
    max_pct = to_decimal(portfolio["max_position_pct"])
    holdings = {
        h["security_id"]: (to_decimal(h["quantity"]), to_decimal(h["market_price"]))
        for h in portfolio["current_holdings"]
    }

    # restricted security
    if security_id in portfolio["restricted_securities"]:
        return _result(REJECTED, "Security is restricted for this portfolio.")

    existing_qty = holdings.get(security_id, (Decimal(0), None))[0]

    # sell check
    if action == "Sell":
        if existing_qty < qty:  # exactly equal is fine
            return _result(REJECTED, "Insufficient holdings to sell.")
        return _result(APPROVED, "Trade passed all checks.")

    # buy affordability
    cost = qty * price
    if cost > cash:  # exactly equal is fine
        return _result(REJECTED, "Insufficient cash for this buy order.")

    # buy only
    post_trade_cash = cash - cost
    this_value = (existing_qty + qty) * price  # trade price = market price
    other_value = sum(
        (q * p for sid, (q, p) in holdings.items() if sid != security_id),
        Decimal(0),
    )
    total_after = post_trade_cash + this_value + other_value
    if total_after <= 0:  
        return _result(MANUAL, "Portfolio value is zero — requires approval.")

    position_pct = this_value / total_after
    if position_pct > max_pct: 
        return _result(
            MANUAL,
            "Exceeds maximum position concentration — requires approval.",
        )

    return _result(APPROVED, "Trade passed all checks.")
