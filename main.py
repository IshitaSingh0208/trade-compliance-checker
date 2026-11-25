"""Run every trade in trades_test.csv through the checker.

Usage:  python main.py [trades.csv] [portfolios.json]
Writes results.csv and prints a table.
"""
import csv
import json
import sys

from checker import check_trade


def main():
    trades_file = sys.argv[1] if len(sys.argv) > 1 else "trades_test.csv"
    portfolios_file = sys.argv[2] if len(sys.argv) > 2 else "portfolios.json"

    with open(portfolios_file, encoding="utf-8") as f:
        portfolios = json.load(f)

    with open(trades_file, newline="", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    rows = []
    for i, trade in enumerate(trades, start=1):
        result = check_trade(trade, portfolios)
        rows.append({**trade, **result})
        print(
            f"{i:>2}. {trade['portfolio_id']} {trade['action']:<4} "
            f"{trade['security_id']:<8} qty={trade['quantity']:<5} "
            f"px={trade['price']:<6} -> {result['decision']:<22} | {result['reason']}"
        )

    fields = list(trades[0].keys()) + ["decision", "reason"]
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved results.csv")


if __name__ == "__main__":
    main()
