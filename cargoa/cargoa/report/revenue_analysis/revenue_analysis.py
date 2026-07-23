# -*- coding: utf-8 -*-
"""Revenue Analysis — by customer and by route."""
import frappe
from frappe import _

def execute(filters=None):
	group_by = filters.get("group_by") or "Customer"
	group_field = "customer" if group_by == "Customer" else "route"
	columns = [
		{"label": _(group_by), "fieldname": group_field, "fieldtype": "Data", "width": 160},
		{"label": _("Trips"), "fieldname": "trips", "fieldtype": "Int", "width": 70},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
		{"label": _("Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Margin %"), "fieldname": "margin", "fieldtype": "Percent", "width": 90},
		{"label": _("Avg Revenue/Trip"), "fieldname": "avg_rev", "fieldtype": "Currency", "width": 130},
	]
	conditions = "where docstatus = 1"
	if filters.get("from_date"):
		conditions += " and trip_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and trip_date <= %(to_date)s"

	rows = frappe.db.sql(f"""
		select {group_field}, count(*) as trips, sum(total_revenue) as revenue,
			sum(total_trip_cost) as cost, sum(trip_profit) as profit
		from `tabFreight Trip` {conditions}
		group by {group_field} order by revenue desc
	""", filters, as_dict=True)

	data = []
	for r in rows:
		margin = (r.profit / r.revenue * 100) if r.revenue else 0
		avg = (r.revenue / r.trips) if r.trips else 0
		data.append({group_field: getattr(r, group_field), "trips": r.trips,
			"revenue": r.revenue, "cost": r.cost, "profit": r.profit,
			"margin": round(margin, 1), "avg_rev": avg})
	return columns, data
