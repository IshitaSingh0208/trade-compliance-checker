from checker import check_trade, APPROVED, REJECTED, MANUAL

PORTFOLIOS = {
    "P": {
        "cash_balance": 10000,
        "restricted_securities": ["BAD"],
        "max_position_pct": 0.20,
        "current_holdings": [
            {"security_id": "AAPL", "quantity": 10, "market_price": 100},
            {"security_id": "MSFT", "quantity": 20, "market_price": 50},
        ],
    }
}


def trade(**kw):
    base = dict(portfolio_id="P", security_id="AAPL", action="Buy",
                quantity=1, price=100, security_type="Equity")
    base.update(kw)
    return check_trade(base, PORTFOLIOS)


# Step 1
def test_negative_quantity():
    r = trade(quantity=-5)
    assert (r["decision"], r["reason"]) == (REJECTED, "Invalid trade data.")

def test_zero_price():
    assert trade(price=0)["reason"] == "Invalid trade data."

def test_bad_action():
    assert trade(action="Hold")["reason"] == "Invalid trade data."

def test_non_numeric_and_bool_and_nan():
    assert trade(quantity="abc")["reason"] == "Invalid trade data."
    assert trade(quantity=True)["reason"] == "Invalid trade data."
    assert trade(price="nan")["reason"] == "Invalid trade data."

# Step 2
def test_restricted():
    r = trade(security_id="BAD")
    assert r["reason"] == "Security is restricted for this portfolio."

# Step 3
def test_sell_exact_holding_ok():
    assert trade(action="Sell", quantity=10)["decision"] == APPROVED

def test_sell_more_than_held():
    r = trade(action="Sell", quantity=11)
    assert (r["decision"], r["reason"]) == (REJECTED, "Insufficient holdings to sell.")

def test_sell_unheld_security():
    assert trade(action="Sell", security_id="TCS")["decision"] == REJECTED

def test_sell_never_triggers_concentration():
    assert trade(action="Sell", quantity=10)["decision"] == APPROVED

# Step 4
def test_buy_exact_cash_is_affordable():
    # 100 x 100 = 10,000 passes step 4 (then hits concentration, not cash)
    assert trade(quantity=100)["reason"] != "Insufficient cash for this buy order."

def test_buy_over_cash():
    r = trade(quantity=101)
    assert (r["decision"], r["reason"]) == (REJECTED, "Insufficient cash for this buy order.")

# Step 5
def test_worked_example_manual_signoff():
    r = trade(quantity=20)  # 25% > 20%
    assert r["decision"] == MANUAL

def test_exactly_at_cap_passes():
    # Buy 20 AAPL @100 -> 3000 / 12000 = exactly 25%; cap set to 25% -> passes
    p = {"P": {**PORTFOLIOS["P"], "max_position_pct": 0.25}}
    t = dict(portfolio_id="P", security_id="AAPL", action="Buy",
             quantity=20, price=100, security_type="Equity")
    assert check_trade(t, p)["decision"] == APPROVED

def test_just_under_cap_passes():
    assert trade(quantity=10)["decision"] == APPROVED  # 2000/12000 = 16.7%

def test_does_not_double_count_existing_position():
    # If AAPL's existing 1000 were counted twice, total would be 13,000 not 12,000
    r = trade(quantity=20)
    assert r["decision"] == MANUAL  # 3000/12000 = 0.25

# Order of checks
def test_step1_beats_step5():
    assert trade(quantity=-1000)["reason"] == "Invalid trade data."

def test_step2_beats_step4():
    assert trade(security_id="BAD", quantity=10_000)["reason"] == \
        "Security is restricted for this portfolio."

# Unknown portfolio (assumption)
def test_unknown_portfolio():
    r = check_trade(dict(portfolio_id="X", security_id="A", action="Buy",
                         quantity=1, price=1), PORTFOLIOS)
    assert r["decision"] == REJECTED
