# -*- coding: utf-8 -*-
import frappe
from frappe import _
def execute(filters=None):
    cols = [
        {"label":_("Driver"),"fieldname":"driver","fieldtype":"Link","options":"Driver","width":130},
        {"label":_("Type"),"fieldname":"driver_type","fieldtype":"Data","width":90},
        {"label":_("Trips"),"fieldname":"trips","fieldtype":"Int","width":60},
        {"label":_("Revenue"),"fieldname":"revenue","fieldtype":"Currency","width":110},
        {"label":_("Allowances"),"fieldname":"allowances","fieldtype":"Currency","width":100},
        {"label":_("Fuel (L)"),"fieldname":"fuel_liters","fieldtype":"Float","width":80},
        {"label":_("Profit"),"fieldname":"profit","fieldtype":"Currency","width":110},
        {"label":_("Margin %"),"fieldname":"margin","fieldtype":"Percent","width":90},
    ]
    cond = "where t.docstatus=1"
    if filters.get("from_date"): cond += " and t.trip_date>=%(from_date)s"
    if filters.get("to_date"): cond += " and t.trip_date<=%(to_date)s"
    rows = frappe.db.sql(f"""select t.driver, d.driver_type, count(*) trips,
        sum(t.total_revenue) revenue, sum(t.total_allowances) allowances,
        sum(t.total_fuel_liters) fuel_liters, sum(t.trip_profit) profit,
        avg(case when t.total_revenue>0 then t.trip_profit/t.total_revenue*100 else 0 end) margin
        from `tabFreight Trip` t left join `tabDriver` d on d.name=t.driver
        {cond} group by t.driver order by revenue desc""", filters, as_dict=True)
    data = [{"driver":r.driver,"driver_type":r.driver_type,"trips":r.trips,"revenue":r.revenue,
        "allowances":r.allowances,"fuel_liters":r.fuel_liters,"profit":r.profit,
        "margin":round(r.margin or 0,1)} for r in rows]
    return cols, data
