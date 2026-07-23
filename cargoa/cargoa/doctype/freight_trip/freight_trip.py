# -*- coding: utf-8 -*-
"""Freight Trip — THE HUB. Rolls up costs -> live P&L."""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

CATEGORY_TO_BUCKET = {
	"Fuel": "total_fuel_cost", "Driver Allowance (Posho)": "total_allowances",
	"Weighbridge Fine": "total_fines_tolls", "Toll Gate": "total_fines_tolls",
	"En-route Repair": "total_repairs", "Offloading Fee": "total_offloading_loading",
	"Loading Fee": "total_offloading_loading", "Truck Hire": "total_truck_hire",
	"Other": "total_other",
}
COST_BUCKETS = ["total_fuel_cost","total_allowances","total_fines_tolls",
	"total_repairs","total_offloading_loading","total_truck_hire","total_other"]
ROLLED = COST_BUCKETS + ["total_trip_cost","trip_profit","profit_margin","total_fuel_liters","fuel_variance_liters"]


class FreightTrip(Document):
	def validate(self):
		self.calculate_revenue()
		self.calculate_costs_and_profit()
		self.validate_benchmarks()

	def before_submit(self):
		s = frappe.get_doc("Cargoa Settings")
		if not self.customer:
			frappe.throw(_("Customer is required before submitting."))
		if not s.get("allow_zero_revenue_trips") and flt(self.total_revenue) <= 0:
			frappe.throw(_("Total Revenue must be greater than zero."))
		self.calculate_costs_and_profit()
		if self.trip_status in ("Draft","Scheduled","In Transit"):
			self.trip_status = "Completed"

	def on_submit(self):
		s = frappe.get_doc("Cargoa Settings")
		if not s.get("auto_create_accounting", 1):
			return
		try:
			from cargoa.cargoa.api import auto_create_accounting
			auto_create_accounting(self.name)
		except Exception:
			frappe.log_error(title="Cargoa auto-accounting trip " + str(self.name))

	def on_cancel(self):
		self.db_set("trip_status", "Cancelled")

	def calculate_revenue(self):
		if not self.is_flat_rate:
			self.total_revenue = flt(self.cargo_weight) * flt(self.agreed_rate)

	def calculate_costs_and_profit(self):
		bd = get_trip_cost_breakdown(self.name)
		for f in ROLLED:
			self.set(f, flt(bd.get(f, 0)))
		self.trip_profit = flt(self.total_revenue) - flt(self.total_trip_cost)
		self.profit_margin = (self.trip_profit / flt(self.total_revenue) * 100.0) if flt(self.total_revenue) else 0
		self.fuel_variance_liters = (flt(self.total_fuel_liters) - flt(self.standard_fuel_allocation)) if flt(self.standard_fuel_allocation) else 0

	def validate_benchmarks(self):
		s = frappe.get_doc("Cargoa Settings")
		if flt(self.standard_fuel_allocation) and flt(self.total_fuel_liters) > flt(self.standard_fuel_allocation):
			frappe.msgprint(_("Warning: fuel ({0} L) exceeds standard ({1} L) by {2} L.").format(
				flt(self.total_fuel_liters), flt(self.standard_fuel_allocation), flt(self.fuel_variance_liters)), indicator="orange")
		if flt(self.standard_driver_allowance) and flt(self.total_allowances) > flt(self.standard_driver_allowance):
			frappe.msgprint(_("Warning: allowances ({0}) exceed standard ({1}).").format(
				fmt_money(self.total_allowances), fmt_money(self.standard_driver_allowance)), indicator="orange")
		if s.get("warn_negative_margin") and flt(self.profit_margin) < 0:
			frappe.msgprint(_("Warning: negative profit margin ({0}%).").format(self.profit_margin), indicator="red")


def get_trip_cost_breakdown(trip_name):
	rows = frappe.db.sql("""select expense_category, sum(amount) amount, sum(quantity) quantity
		from `tabTrip Expense` where freight_trip=%s and docstatus=1 group by expense_category""", trip_name, as_dict=True)
	out = {f: 0.0 for f in ROLLED}
	for r in rows:
		bucket = CATEGORY_TO_BUCKET.get(r.expense_category, "total_other")
		out[bucket] += flt(r.amount)
		if r.expense_category == "Fuel":
			out["total_fuel_liters"] += flt(r.quantity or 0)
	out["total_trip_cost"] = sum(out[f] for f in COST_BUCKETS)
	return out


def update_trip_costs(trip_name):
	if not trip_name or not frappe.db.exists("Freight Trip", trip_name):
		return
	try:
		trip = frappe.get_doc("Freight Trip", trip_name)
		trip.calculate_costs_and_profit()
		frappe.db.set_value("Freight Trip", trip_name, {f: trip.get(f) for f in ROLLED}, update_modified=False)
	except Exception:
		frappe.log_error(title="Cargoa update_trip_costs " + str(trip_name))
