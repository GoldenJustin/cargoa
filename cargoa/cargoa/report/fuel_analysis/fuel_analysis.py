# -*- coding: utf-8 -*-
"""Fuel Analysis — consumption vs benchmark, variance, cost per km."""
import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Trip"), "fieldname": "trip", "fieldtype": "Link", "options": "Freight Trip", "width": 140},
		{"label": _("Date"), "fieldname": "trip_date", "fieldtype": "Date", "width": 90},
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 110},
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Data", "width": 130},
		{"label": _("Distance (km)"), "fieldname": "distance", "fieldtype": "Float", "width": 100},
		{"label": _("Actual (L)"), "fieldname": "actual", "fieldtype": "Float", "width": 90},
		{"label": _("Standard (L)"), "fieldname": "standard", "fieldtype": "Float", "width": 90},
		{"label": _("Variance (L)"), "fieldname": "variance", "fieldtype": "Float", "width": 90},
		{"label": _("km/L"), "fieldname": "efficiency", "fieldtype": "Float", "width": 70},
		{"label": _("Fuel Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Cost/km"), "fieldname": "cost_per_km", "fieldtype": "Currency", "width": 90},
	]
	conditions = "where docstatus = 1"
	if filters.get("from_date"):
		conditions += " and trip_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and trip_date <= %(to_date)s"

	rows = frappe.db.sql(f"""
		select name, trip_date, prime_mover, route, distance_km,
			total_fuel_liters, standard_fuel_allocation, fuel_variance_liters,
			total_fuel_cost
		from `tabFreight Trip` {conditions}
		order by trip_date desc
	""", filters, as_dict=True)

	data = []
	for r in rows:
		eff = (r.distance_km / r.total_fuel_liters) if r.total_fuel_liters else 0
		cpk = (r.total_fuel_cost / r.distance_km) if r.distance_km else 0
		data.append({"trip": r.name, "trip_date": r.trip_date, "vehicle": r.prime_mover,
			"route": r.route, "distance": r.distance_km, "actual": r.total_fuel_liters,
			"standard": r.standard_fuel_allocation, "variance": r.fuel_variance_liters,
			"efficiency": round(eff, 2), "cost": r.total_fuel_cost, "cost_per_km": round(cpk, 2)})
	return columns, data
