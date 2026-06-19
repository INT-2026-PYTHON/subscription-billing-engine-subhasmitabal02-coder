"""
CLI entrypoint.

Subcommands to implement (Day 4):
    billing init                              -- create / migrate the DB
    billing customer add <name> <email> <country> [--state CODE]
    billing plan list
    billing subscribe <customer_id> <plan_id> [--trial-days N] [--discount CODE]
    billing bill run [--date YYYY-MM-DD]
    billing invoice show <invoice_id>          -- prints PLAIN TEXT invoice
    billing upgrade <subscription_id> <new_plan_id> [--date YYYY-MM-DD]   (STRETCH)
    billing demo                              -- run the scripted scenario

Use argparse with subparsers. Keep each subcommand handler in its own function.

PDF rendering is OUT OF SCOPE for the core project — `invoice show` should
print a clean PLAIN-TEXT invoice (see helper `format_invoice_text` below).
PDF generation is BONUS: see `billing_engine/pdf/renderer.py`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from billing_engine.models import Invoice


def format_invoice_text(invoice: Invoice, customer_name: str, plan_name: str) -> str:
    """Render an invoice as a plain-text receipt. Pure function — easy to test."""
    lines = []
    lines.append(f"INVOICE #{invoice.id}")
    lines.append("=" * 60)

    lines.append(f"Customer: {customer_name}")
    lines.append(f"Plan:     {plan_name}")
    lines.append(f"Period:   {invoice.period_start} to {invoice.period_end}")
    lines.append("-" * 60)

    subtotal = 0

    for item in invoice.line_items:
        amount = float(item.amount)
        subtotal += amount

        lines.append(f"{item.description:<45} ₹ {amount:10.2f}")

    lines.append("-" * 60)

    discount = float(getattr(invoice, "discount_total", 0))
    tax = float(getattr(invoice, "tax_total", 0))
    total = float(getattr(invoice, "total", subtotal + tax - discount))

    if discount:
        lines.append(f"Discount{'':<38} ₹ {discount:10.2f}")
    if tax:
        lines.append(f"Tax{'':<43} ₹ {tax:10.2f}")

    lines.append("-" * 60)
    lines.append(f"{'TOTAL':<45} ₹ {total:10.2f}")
    lines.append(f"Status: {invoice.status}")

    return "\n".join(lines)    


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="billing", description="Subscription Billing CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    

    sub.add_parser("init", help="initialize the database")
    sub.add_parser("demo", help="run the demo scenario")
    customer_add = sub.add_parser("customer")
    customer_sub = customer_add.add_subparsers(dest="action", required=True)

    add = customer_sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("email")
    add.add_argument("country")
    add.add_argument("--state")

    sub.add_parser("plan").add_argument("list")
    subscribe = sub.add_parser("subscribe")
    subscribe.add_argument("customer_id", type=int)
    subscribe.add_argument("plan_id", type=int)
    subscribe.add_argument("--trial-days", type=int, default=0)
    subscribe.add_argument("--discount")
    bill = sub.add_parser("bill")
    bill_sub = bill.add_subparsers(dest="action", required=True)
    run = bill_sub.add_parser("run")
    run.add_argument("--date")

    invoice = sub.add_parser("invoice")
    invoice_sub = invoice.add_subparsers(dest="action", required=True)
    show = invoice_sub.add_parser("show")
    show.add_argument("invoice_id", type=int)

    upgrade = sub.add_parser("upgrade")
    upgrade.add_argument("subscription_id", type=int)
    upgrade.add_argument("new_plan_id", type=int)
    upgrade.add_argument("--date")



    args = parser.parse_args(argv)
    print(f"TODO: implement command '{args.cmd}'", file=sys.stderr)
    return 2


def run_demo() -> int:
    """Scripted end-to-end scenario for the `demo` subcommand.

    Should mirror `tests/test_demo_scenario.py::TestEndToEndScenario::test_full_lifecycle`
    and print a human-readable summary to stdout.
    """
    print("=== Billing Engine Demo ===")

    print("1. Initializing database...")
    print("2. Creating customer...")
    print("3. Creating subscription...")
    print("4. Running billing cycle...")
    print("5. Generating invoice...")
    print("6. Performing upgrade...")
    print("7. Running dunning process...")
    print("=== Demo complete ===")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
