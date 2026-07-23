# -*- coding: utf-8 -*-
"""Shared utility functions for Cargoa."""
import frappe
from frappe.utils import flt


def get_settings():
	"""Get Cargoa Settings (Single doctype, always loadable)."""
	return frappe.get_doc("Cargoa Settings")


def compute_route_tariff(route, weight):
	"""Look up the best-matching Tariff for a route and compute the cost.
	Returns (tariff_name, amount)."""
	amount = 0
	tariff_name = None
	# Try route-specific, active tariffs ordered by priority
	tariffs = frappe.db.sql("""
		select name, rate_type, base_rate, min_charge
		from `tabTariff`
		where (route = %s or route is null) and is_active = 1
		order by (case when route = %s then 0 else 1 end), valid_from desc
		limit 1
	""", (route or "", route or ""), as_dict=True)
	if tariffs:
		t = tariffs[0]
		tariff_name = t["name"]
		if t["rate_type"] == "Per Ton":
			amount = flt(weight) * flt(t["base_rate"])
		elif t["rate_type"] == "Flat":
			amount = flt(t["base_rate"])
		else:
			amount = flt(t["base_rate"])
		if flt(t["min_charge"]) > amount:
			amount = flt(t["min_charge"])
	return tariff_name, amount


def get_or_create_tracking(trip_name):
	"""Ensure a Shipment Tracking record exists for a trip. Returns name or None."""
	try:
		existing = frappe.db.get_value("Shipment Tracking", {"freight_trip": trip_name})
		if existing:
			return existing
		trk = frappe.new_doc("Shipment Tracking")
		trk.freight_trip = trip_name
		trk.status = "Booked"
		trk.insert(ignore_permissions=True)
		return trk.name
	except Exception:
		return None
