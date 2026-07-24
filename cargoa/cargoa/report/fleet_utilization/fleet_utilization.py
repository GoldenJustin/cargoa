# -*- coding: utf-8 -*-
import frappe
from frappe import _
def execute(filters=None):
    cols = [
        {"label":_("Vehicle"),"fieldname":"vehicle","fieldtype":"Link","options":"Transport Vehicle","width":120},
        {"label":_("Type"),"fieldname":"vehicle_type","fieldtype":"Data","width":80},
        {"label":_("Ownership"),"fieldname":"ownership","fieldtype":"Data","width":80},
        {"label":_("Trips"),"fieldname":"trips","fieldtype":"Int","width":60},
        {"label":_("Distance (km)"),"fieldname":"distance","fieldtype":"Float","width":100},
        {"label":_("Revenue"),"fieldname":"revenue","fieldtype":"Currency","width":110},
        {"label":_("Cost"),"fieldname":"cost","fieldtype":"Currency","width":110},
        {"label":_("Profit"),"fieldname":"profit","fieldtype":"Currency","width":110},
        {"label":_("Profit/Km"),"fieldname":"ppk","fieldtype":"Currency","width":90},
    ]
    cond = "where t.docstatus=1"
    if filters.get("from_date"): cond += " and t.trip_date>=%(from_date)s"
    if filters.get("to_date"): cond += " and t.trip_date<=%(to_date)s"
    rows = frappe.db.sql(f"""select t.prime_mover vehicle, v.vehicle_type, v.ownership_type ownership,
        count(*) trips, sum(t.distance_km) distance, sum(t.total_revenue) revenue,
        sum(t.total_trip_cost) cost, sum(t.trip_profit) profit
        from `tabFreight Trip` t left join `tabTransport Vehicle` v on v.name=t.prime_mover
        {cond} group by t.prime_mover order by revenue desc""", filters, as_dict=True)
    data = [{"vehicle":r.vehicle,"vehicle_type":r.vehicle_type,"ownership":r.ownership,
        "trips":r.trips,"distance":r.distance,"revenue":r.revenue,"cost":r.cost,
        "profit":r.profit,"ppk":(r.profit/r.distance if r.distance else 0)} for r in rows]
    return cols, data
