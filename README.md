# Portfolio Trade Order Compliance & Execution Checker

Checks each proposed trade against six ordered rules and returns
**Approved**, **Rejected** or **Needs Manual Sign-off** with a reason.
Spec: `trade_compliance_requirements.md`.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py            # reads trades_test.csv + portfolios.json, writes results.csv
python -m pytest -q       # run the tests
```

## Files
- `checker.py` – `check_trade(trade, portfolios)`; the six steps as early returns
- `main.py` – reads the trades CSV, prints a table, writes `results.csv`
- `portfolios.json` – portfolio reference data (see note below)
- `test_checker.py` – tests per step, per exact-equality boundary and for check ordering

## Assumptions
- **Portfolio data:** the task files did not include reference data for POR001–POR005,
  so `portfolios.json` contains **sample data I created**. Replace it with the official
  data if provided; the code needs no changes.
- Unknown `portfolio_id` -> Rejected, "Unknown portfolio."
- `action` is case-insensitive ("buy" = "Buy").
- Money uses `Decimal`; booleans, NaN and non-numeric values are invalid trade data.
- `security_type` is accepted but no rule uses it.
- Approved trades show the reason "Trade passed all checks."
