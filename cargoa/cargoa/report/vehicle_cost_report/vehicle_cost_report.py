# -*- coding: utf-8 -*-
"""Vehicle Cost Report — operating + maintenance costs per vehicle."""
import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Transport Vehicle", "width": 130},
		{"label": _("Type"), "fieldname": "vehicle_type", "fieldtype": "Data", "width": 90},
		{"label": _("Trips"), "fieldname": "trips", "fieldtype": "Int", "width": 70},
		{"label": _("Trip Expenses"), "fieldname": "trip_costs", "fieldtype": "Currency", "width": 120},
		{"label": _("Service Costs"), "fieldname": "service_costs", "fieldtype": "Currency", "width": 120},
		{"label": _("Fuel Logs"), "fieldname": "fuel_costs", "fieldtype": "Currency", "width": 110},
		{"label": _("Total Cost"), "fieldname": "total", "fieldtype": "Currency", "width": 120},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Net"), "fieldname": "net", "fieldtype": "Currency", "width": 120},
	]
	vehicles = frappe.db.sql("""
		select name, vehicle_type from `tabTransport Vehicle` where is_active = 1
	""", as_dict=True)

	data = []
	for v in vehicles:
		trips = frappe.db.sql("""
			select count(*) as cnt, coalesce(sum(total_trip_cost),0) as costs,
				coalesce(sum(total_revenue),0) as rev
			from `tabFreight Trip` where prime_mover = %s and docstatus = 1
		""", v.name, as_dict=True)[0]
		service = frappe.db.sql("""
			select coalesce(sum(cost),0) from `tabVehicle Service Log`
			where vehicle = %s and docstatus = 1
		""", v.name)[0][0] or 0
		fuel = frappe.db.sql("""
			select coalesce(sum(total_amount),0) from `tabFuel Log`
			where vehicle = %s and docstatus = 1
		""", v.name)[0][0] or 0

		tc = flt(trips["costs"]) if trips else 0
		rev = flt(trips["rev"]) if trips else 0
		trip_count = trips["cnt"] if trips else 0
		total = tc + service + fuel
		data.append({"vehicle": v.name, "vehicle_type": v.vehicle_type,
			"trips": trip_count, "trip_costs": tc, "service_costs": service,
			"fuel_costs": fuel, "total": total, "revenue": rev, "net": rev - total})
	return columns, data

from frappe.utils import flt
