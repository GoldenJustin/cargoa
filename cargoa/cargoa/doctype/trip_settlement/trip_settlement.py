# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt

TRIP_FIELDS = ["customer","route","driver","prime_mover","trip_date","total_revenue",
	"total_trip_cost","profit_margin","sales_invoice","purchase_invoice","driver_payment"]

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
		data = frappe.db.get_value("Freight Trip", self.freight_trip, TRIP_FIELDS, as_dict=True)
		if data:
			for f in TRIP_FIELDS:
				self.set(f, data.get(f))
			if not self.company:
				self.company = frappe.db.get_value("Freight Trip", self.freight_trip, "company")

	def calculate_totals(self):
		self.customer_balance = flt(self.total_revenue) - flt(self.amount_received)
		self.outstanding_costs = flt(self.total_trip_cost) - flt(self.amounts_paid_out)
		self.net_profit = flt(self.total_revenue) - flt(self.total_trip_cost)
		self.net_cash_position = flt(self.amount_received) - flt(self.amounts_paid_out)
