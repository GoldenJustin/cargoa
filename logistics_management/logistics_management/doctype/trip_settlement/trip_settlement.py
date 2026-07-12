# -*- coding: utf-8 -*-
"""
Trip Settlement - the reconciliation layer that sits on top of a Freight Trip.

The Freight Trip tells you the ACCRUAL picture (Revenue - Cost = Profit).
The Trip Settlement tells you the CASH picture for the same journey:

    Money In  : what the customer has actually paid (Payment Entries)
    Money Out : what the company has actually paid (truck hire, driver, fuel)
    => Net cash position of the journey.

It also surfaces the whole accounting chain on one screen
(Sales Invoice -> Payment, Purchase Invoice -> Payment, Journal Entries),
so you can see exactly where the money is in the process.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

TRIP_SUMMARY_FIELDS = [
	"customer", "route", "driver", "prime_mover", "trip_date",
	"total_revenue", "total_trip_cost", "profit_margin",
	"sales_invoice", "purchase_invoice", "driver_payment",
]


class TripSettlement(Document):
	def validate(self):
		self.fetch_trip_data()
		self.calculate_totals()

	def before_submit(self):
		self.status = "Settled"

	def on_cancel(self):
		self.db_set("status", "Draft")

	def fetch_trip_data(self):
		if not self.freight_trip:
			return
		data = frappe.db.get_value("Freight Trip", self.freight_trip, TRIP_SUMMARY_FIELDS, as_dict=True)
		if not data:
			return
		for field in TRIP_SUMMARY_FIELDS:
			self.set(field, data.get(field))
		if not self.company:
			self.company = frappe.db.get_value("Freight Trip", self.freight_trip, "company")

	def calculate_totals(self):
		self.customer_balance = flt(self.total_revenue) - flt(self.amount_received)
		self.outstanding_costs = flt(self.total_trip_cost) - flt(self.amounts_paid_out)
		self.net_profit = flt(self.total_revenue) - flt(self.total_trip_cost)
		self.net_cash_position = flt(self.amount_received) - flt(self.amounts_paid_out)
