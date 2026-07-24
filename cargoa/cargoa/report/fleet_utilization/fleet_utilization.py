# -*- coding: utf-8 -*-
"""Fleet Utilization — trips, revenue, distance per vehicle."""
import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Transport Vehicle", "width": 130},
		{"label": _("Type"), "fieldname": "vehicle_type", "fieldtype": "Data", "width": 90},
		{"label": _("Ownership"), "fieldname": "ownership", "fieldtype": "Data", "width": 80},
		{"label": _("Trips"), "fieldname": "trips", "fieldtype": "Int", "width": 70},
		{"label": _("Distance (km)"), "fieldname": "distance", "fieldtype": "Float", "width": 110},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
		{"label": _("Profit/Km"), "fieldname": "profit_per_km", "fieldtype": "Currency", "width": 100},
	]
	conditions = "where t.docstatus = 1"
	if filters.get("from_date"):
		conditions += " and t.trip_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and t.trip_date <= %(to_date)s"

	rows = frappe.db.sql(f"""
		select t.prime_mover as vehicle, v.vehicle_type, v.ownership_type as ownership,
			count(*) as trips, sum(t.distance_km) as distance,
			sum(t.total_revenue) as revenue, sum(t.total_trip_cost) as cost,
			sum(t.trip_profit) as profit
		from `tabFreight Trip` t
		left join `tabTransport Vehicle` v on v.name = t.prime_mover
		{conditions}
		group by t.prime_mover order by revenue desc
	""", filters, as_dict=True)

	data = []
	for r in rows:
		profit_per_km = (r.profit / r.distance) if r.distance else 0
		data.append({"vehicle": r.vehicle, "vehicle_type": r.vehicle_type, "ownership": r.ownership,
			"trips": r.trips, "distance": r.distance, "revenue": r.revenue, "cost": r.cost,
			"profit": r.profit, "profit_per_km": profit_per_km})
	return columns, data
