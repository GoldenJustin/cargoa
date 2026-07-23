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
	conditions = "where docstatus = 1"
	if filters.get("from_date"):
		conditions += " and t.trip_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and t.trip_date <= %(to_date)s"

	vehicles = frappe.db.sql("""
		select name, vehicle_type from `tabTransport Vehicle` where is_active = 1
	""", as_dict=True)

	data = []
	for v in vehicles:
		trip_data = frappe.db.sql(f"""
			select count(*) as trips, sum(total_trip_cost) as trip_costs, sum(total_revenue) as revenue
			from `tabFreight Trip` where prime_mover = %s {conditions.replace('where', 'and').replace('t.', '')}
		""", v.name, as_dict=True)
		service = frappe.db.sql("select coalesce(sum(cost),0) from `tabVehicle Service Log` where vehicle = %s and docstatus = 1", v.name)[0][0]
		fuel = frappe.db.sql("select coalesce(sum(total_amount),0) from `tabFuel Log` where vehicle = %s and docstatus = 1", v.name)[0][0]
		trips = trip_data[0]["trips"] or 0 if trip_data else 0
		tc = trip_data[0]["trip_costs"] or 0 if trip_data else 0
		rev = trip_data[0]["revenue"] or 0 if trip_data else 0
		total = tc + service + fuel
		data.append({"vehicle": v.name, "vehicle_type": v.vehicle_type, "trips": trips,
			"trip_costs": tc, "service_costs": service, "fuel_costs": fuel,
			"total": total, "revenue": rev, "net": rev - total})
	return columns, data
