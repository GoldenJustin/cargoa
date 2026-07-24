# -*- coding: utf-8 -*-
import frappe
from frappe import _
def execute(filters=None):
    cols = [
        {"label":_("Trip"),"fieldname":"trip","fieldtype":"Link","options":"Freight Trip","width":130},
        {"label":_("Date"),"fieldname":"trip_date","fieldtype":"Date","width":80},
        {"label":_("Route"),"fieldname":"route","fieldtype":"Data","width":130},
        {"label":_("Customer"),"fieldname":"customer","fieldtype":"Link","options":"Customer","width":120},
        {"label":_("Vehicle"),"fieldname":"prime_mover","fieldtype":"Data","width":100},
        {"label":_("Revenue"),"fieldname":"revenue","fieldtype":"Currency","width":100},
        {"label":_("Fuel"),"fieldname":"fuel","fieldtype":"Currency","width":80},
        {"label":_("Allowances"),"fieldname":"allowances","fieldtype":"Currency","width":90},
        {"label":_("Fines/Tolls"),"fieldname":"fines","fieldtype":"Currency","width":80},
        {"label":_("Repairs"),"fieldname":"repairs","fieldtype":"Currency","width":80},
        {"label":_("Load/Off"),"fieldname":"loadoff","fieldtype":"Currency","width":90},
        {"label":_("Truck Hire"),"fieldname":"hire","fieldtype":"Currency","width":80},
        {"label":_("Other"),"fieldname":"other","fieldtype":"Currency","width":70},
        {"label":_("Total Cost"),"fieldname":"total_cost","fieldtype":"Currency","width":100},
        {"label":_("Profit"),"fieldname":"profit","fieldtype":"Currency","width":100},
        {"label":_("Margin %"),"fieldname":"margin","fieldtype":"Percent","width":70},
    ]
    cond = "where docstatus=1"
    if filters.get("from_date"): cond += " and trip_date>=%(from_date)s"
    if filters.get("to_date"): cond += " and trip_date<=%(to_date)s"
    if filters.get("route"): cond += " and route=%(route)s"
    if filters.get("customer"): cond += " and customer=%(customer)s"
    rows = frappe.db.sql(f"""select name,trip_date,route,customer,prime_mover,total_revenue,
        total_fuel_cost,total_allowances,total_fines_tolls,total_repairs,total_offloading_loading,
        total_truck_hire,total_other,total_trip_cost,trip_profit,
        case when total_revenue>0 then round(trip_profit/total_revenue*100,1) else 0 end margin
        from `tabFreight Trip` {cond} order by trip_date desc""", filters, as_dict=True)
    data = [{"trip":r.name,"trip_date":r.trip_date,"route":r.route,"customer":r.customer,
        "prime_mover":r.prime_mover,"revenue":r.total_revenue,"fuel":r.total_fuel_cost,
        "allowances":r.total_allowances,"fines":r.total_fines_tolls,"repairs":r.total_repairs,
        "loadoff":r.total_offloading_loading,"hire":r.total_truck_hire,"other":r.total_other,
        "total_cost":r.total_trip_cost,"profit":r.trip_profit,"margin":r.margin} for r in rows]
    return cols, data
