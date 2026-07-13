# -*- coding: utf-8 -*-
"""
Freight Trip - THE HUB.

Everything revolves around this document:
  * it links Route + Vehicle(s) + Driver + Waybill
  * it pulls in all Trip Expenses (the spokes) and rolls them up into a
    real-time Profit & Loss for the journey
  * it is the launch point for the whole accounting / money-flow chain
    (Sales Invoice -> Payment Entry, Purchase Invoice, Journal Entry, ...)

The cost roll-up is recalculated:
  * every time the trip is saved/validated (in-memory, sets fields), and
  * every time a Trip Expense is submitted/cancelled (persisted via
    ``update_trip_costs`` below).
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

# Maps a Trip Expense category to the bucket field on the Freight Trip.
CATEGORY_TO_BUCKET = {
	"Fuel": "total_fuel_cost",
	"Driver Allowance (Posho)": "total_allowances",
	"Weighbridge Fine": "total_fines_tolls",
	"Toll Gate": "total_fines_tolls",
	"En-route Repair": "total_repairs",
	"Offloading Fee": "total_offloading_loading",
	"Loading Fee": "total_offloading_loading",
	"Truck Hire": "total_truck_hire",
	"Other": "total_other",
}

COST_BUCKET_FIELDS = [
	"total_fuel_cost",
	"total_allowances",
	"total_fines_tolls",
	"total_repairs",
	"total_offloading_loading",
	"total_truck_hire",
	"total_other",
]

# All read-only cost / profit fields that get re-computed.
ROLLED_UP_FIELDS = COST_BUCKET_FIELDS + [
	"total_trip_cost",
	"trip_profit",
	"profit_margin",
	"total_fuel_liters",
	"fuel_variance_liters",
]


class FreightTrip(Document):
	# --------------------------------------------------------------
	# Validation / lifecycle
	# --------------------------------------------------------------
	def validate(self):
		self.calculate_revenue()
		self.calculate_costs_and_profit()
		self.validate_benchmarks()

	def before_submit(self):
		settings = frappe.get_doc("Logistics Settings")
		if not self.customer:
			frappe.throw(_("Customer is required before submitting a Freight Trip."))
		if not settings.allow_zero_revenue_trips and flt(self.total_revenue) <= 0:
			frappe.throw(_("Total Revenue must be greater than zero before submitting."))
		self.calculate_costs_and_profit()
		if self.trip_status in ("Draft", "Scheduled", "In Transit"):
			self.trip_status = "Completed"

	def on_submit(self):
		"""Auto-create accounting vouchers (Sales Invoice, Purchase Invoice,
		Driver Payment) if enabled in Logistics Settings."""
		settings = frappe.get_doc("Logistics Settings")
		if not settings.get("auto_create_accounting", 1):
			return
		try:
			from logistics_management.logistics_management.api import auto_create_accounting
			auto_create_accounting(self.name)
		except Exception:
			frappe.log_error(title="Logistics: auto-accounting for trip " + str(self.name))

	def on_cancel(self):
		self.db_set("trip_status", "Cancelled")

	# --------------------------------------------------------------
	# Calculations
	# --------------------------------------------------------------
	def calculate_revenue(self):
		if not self.is_flat_rate:
			self.total_revenue = flt(self.cargo_weight) * flt(self.agreed_rate)

	def calculate_costs_and_profit(self):
		breakdown = get_trip_cost_breakdown(self.name)
		for field in ROLLED_UP_FIELDS:
			self.set(field, flt(breakdown.get(field, 0)))

		self.trip_profit = flt(self.total_revenue) - flt(self.total_trip_cost)
		self.profit_margin = (
			(self.trip_profit / flt(self.total_revenue) * 100.0) if flt(self.total_revenue) else 0
		)

		if flt(self.standard_fuel_allocation):
			self.fuel_variance_liters = flt(self.total_fuel_liters) - flt(self.standard_fuel_allocation)
		else:
			self.fuel_variance_liters = 0

	def validate_benchmarks(self):
		settings = frappe.get_doc("Logistics Settings")

		# Fuel over-consumption
		if (
			flt(self.standard_fuel_allocation)
			and flt(self.total_fuel_liters) > flt(self.standard_fuel_allocation)
		):
			frappe.msgprint(
				_(
					"Warning: fuel drawn ({0} L) exceeds the route's standard allocation "
					"({1} L) by {2} L. Possible theft or excess consumption."
				).format(
					flt(self.total_fuel_liters),
					flt(self.standard_fuel_allocation),
					flt(self.fuel_variance_liters),
				),
				indicator="orange",
			)

		# Driver allowance over standard
		if (
			flt(self.standard_driver_allowance)
			and flt(self.total_allowances) > flt(self.standard_driver_allowance)
		):
			frappe.msgprint(
				_(
					"Warning: driver allowances ({0}) exceed the route's standard "
					"allowance ({1})."
				).format(
					fmt_money(self.total_allowances),
					fmt_money(self.standard_driver_allowance),
				),
				indicator="orange",
			)

		# Negative margin
		if settings.warn_negative_margin and flt(self.profit_margin) < 0:
			frappe.msgprint(
				_("Warning: this trip has a negative profit margin ({0}%).").format(
					self.profit_margin
				),
				indicator="red",
			)


# ------------------------------------------------------------------
# Module-level helpers (also called from Trip Expense, Waybill, hooks)
# ------------------------------------------------------------------
def get_trip_cost_breakdown(trip_name):
	"""Return a dict of the rolled-up cost fields for a trip, based on
	submitted Trip Expenses."""
	rows = frappe.db.sql(
		"""
		select expense_category, sum(amount) as amount, sum(quantity) as quantity
		from `tabTrip Expense`
		where freight_trip = %s and docstatus = 1
		group by expense_category
		""",
		trip_name,
		as_dict=True,
	)

	out = {field: 0.0 for field in ROLLED_UP_FIELDS}

	for row in rows:
		bucket = CATEGORY_TO_BUCKET.get(row.expense_category, "total_other")
		out[bucket] += flt(row.amount)
		if row.expense_category == "Fuel":
			out["total_fuel_liters"] += flt(row.quantity or 0)

	out["total_trip_cost"] = sum(out[field] for field in COST_BUCKET_FIELDS)
	return out


def update_trip_costs(trip_name):
	"""Recompute and PERSIST the cost/profit figures on a trip.

	Called from Trip Expense on_submit / on_cancel and from the accounting
	on_cancel hook so the trip's P&L stays live even after the trip itself has
	already been submitted.
	"""
	if not trip_name or not frappe.db.exists("Freight Trip", trip_name):
		return

	trip = frappe.get_doc("Freight Trip", trip_name)
	trip.calculate_costs_and_profit()

	values = {field: trip.get(field) for field in ROLLED_UP_FIELDS}
	frappe.db.set_value("Freight Trip", trip_name, values, update_modified=False)
