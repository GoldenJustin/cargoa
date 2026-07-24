# -*- coding: utf-8 -*-
import frappe
from frappe import _
def execute(filters=None):
    gb = filters.get("group_by") or "Customer"
    gf = "customer" if gb=="Customer" else "route"
    cols = [
        {"label":_(gb),"fieldname":gf,"fieldtype":"Data","width":150},
        {"label":_("Trips"),"fieldname":"trips","fieldtype":"Int","width":60},
        {"label":_("Revenue"),"fieldname":"revenue","fieldtype":"Currency","width":120},
        {"label":_("Cost"),"fieldname":"cost","fieldtype":"Currency","width":120},
        {"label":_("Profit"),"fieldname":"profit","fieldtype":"Currency","width":120},
        {"label":_("Margin %"),"fieldname":"margin","fieldtype":"Percent","width":80},
        {"label":_("Avg Rev/Trip"),"fieldname":"avg_rev","fieldtype":"Currency","width":120},
    ]
    cond = "where docstatus=1"
    if filters.get("from_date"): cond += " and trip_date>=%(from_date)s"
    if filters.get("to_date"): cond += " and trip_date<=%(to_date)s"
    rows = frappe.db.sql(f"""select {gf}, count(*) trips, sum(total_revenue) revenue,
        sum(total_trip_cost) cost, sum(trip_profit) profit
        from `tabFreight Trip` {cond} group by {gf} order by revenue desc""", filters, as_dict=True)
    data = []
    for r in rows:
        m = (r.profit/r.revenue*100) if r.revenue else 0
        a = (r.revenue/r.trips) if r.trips else 0
        row = {"trips":r.trips,"revenue":r.revenue,"cost":r.cost,"profit":r.profit,"margin":round(m,1),"avg_rev":a}
        row[gf] = getattr(r, gf)
        data.append(row)
    return cols, data
