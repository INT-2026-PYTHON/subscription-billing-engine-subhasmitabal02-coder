"""
BillingCycle — finds due subscriptions, generates invoices, posts ledger DEBITs,
advances the subscription period. Must be IDEMPOTENT (safe to run twice).
"""

from __future__ import annotations

import calendar
import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Callable

from billing_engine.billing.pipeline import build_invoice
from billing_engine.db import (
    Database,
    CustomerRepository, PlanRepository, SubscriptionRepository,
    UsageRecordRepository, InvoiceRepository, InvoiceLineItemRepository,
    LedgerRepository,
)
from billing_engine.models import (
    BillingPeriod,
    InvoiceLineItem,
    InvoiceStatus,
    LedgerDirection,
    LedgerEntry,
    Subscription,
    SubscriptionStatus,
)



@dataclass
class BillingResult:
    invoices_created: int
    invoices_skipped_duplicate: int
    trials_activated: int

        

class BillingCycle:
    """Day-3 deliverable. Day-4 stretch: add `upgrade_subscription(...)`."""

    def __init__(
        self,
        db: Database,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
        subscription_repo: SubscriptionRepository,
        usage_repo: UsageRecordRepository,
        invoice_repo: InvoiceRepository,
        line_item_repo: InvoiceLineItemRepository,
        ledger_repo: LedgerRepository,
        strategy_factory: Callable,    # given a Plan, returns a PricingStrategy
        discount_factory: Callable,    # given a discount_id or None, returns a Discount or None
        tax_factory: Callable,         
    ) -> None:
        self.db = db
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.usage_repo = usage_repo
        self.invoice_repo = invoice_repo
        self.line_item_repo = line_item_repo
        self.ledger_repo = ledger_repo
        self.strategy_factory = strategy_factory
        self.discount_factory = discount_factory
        self.tax_factory = tax_factory

    
    def run(self, as_of: date) -> BillingResult:
        """Bill all subscriptions whose current period ends on or before `as_of`."""


    def upgrade_subscription(self, subscription_id: int, new_plan_id: int, switch_date: date) -> None:
        """Mid-cycle upgrade — Day 4 stretch."""
        subscription: Subscription = self.subscription_repo.get(subscription_id)

        if subscription is None:
            raise ValueError("Subscription not found")

        old_plan = self.plan_repo.get(subscription.plan_id)
        new_plan = self.plan_repo.get(new_plan_id)

        if old_plan is None or new_plan is None:
            raise ValueError("Plan not found")
        
        if not (subscription.current_period_start <= switch_date <= subscription.current_period_end):
            raise ValueError("switch_date must be within current billing period")

        tax_calc, tax_context = self.tax_factory(
        self.customer_repo.get(subscription.customer_id)
    )
        proration = self.proration_service.compute_proration(
        old_plan_price=old_plan.price,
        new_plan_price=new_plan.price,
        period_start=subscription.current_period_start,
        period_end=subscription.current_period_end,
        switch_date=switch_date,
        tax_calc=tax_calc,
        tax_context=tax_context,
    )
    

        self.ledger_repo.add_entry(
        LedgerEntry(
        id=None,
        invoice_id=None,
        customer_id=subscription.customer_id,
        amount=proration.credit_amount,
        direction=LedgerDirection.CREDIT,
        reason="Proration credit - unused old plan portion",
    )
)

        self.ledger_repo.add_entry(
        LedgerEntry(
        id=None,
        invoice_id=None,
        customer_id=subscription.customer_id,
        amount=proration.charge_amount,
        direction=LedgerDirection.DEBIT,
        reason="Proration charge - new plan upgrade",
    )
)
        self.subscription_repo.update(
        subscription_id,
        plan_id=new_plan_id,
        last_switch_date=switch_date,
    )

