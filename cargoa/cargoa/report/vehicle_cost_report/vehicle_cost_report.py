# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.utils import flt
def execute(filters=None):
    cols = [
        {"label":_("Vehicle"),"fieldname":"vehicle","fieldtype":"Link","options":"Transport Vehicle","width":120},
        {"label":_("Type"),"fieldname":"vehicle_type","fieldtype":"Data","width":80},
        {"label":_("Trips"),"fieldname":"trips","fieldtype":"Int","width":60},
        {"label":_("Trip Costs"),"fieldname":"trip_costs","fieldtype":"Currency","width":110},
        {"label":_("Service"),"fieldname":"service_costs","fieldtype":"Currency","width":110},
        {"label":_("Fuel"),"fieldname":"fuel_costs","fieldtype":"Currency","width":100},
        {"label":_("Total"),"fieldname":"total","fieldtype":"Currency","width":110},
        {"label":_("Revenue"),"fieldname":"revenue","fieldtype":"Currency","width":110},
        {"label":_("Net"),"fieldname":"net","fieldtype":"Currency","width":110},
    ]
    vehicles = frappe.db.sql("select name, vehicle_type from `tabTransport Vehicle` where is_active=1", as_dict=True)
    data = []
    for v in vehicles:
        td = frappe.db.sql("select count(*) cnt, coalesce(sum(total_trip_cost),0) costs, coalesce(sum(total_revenue),0) rev from `tabFreight Trip` where prime_mover=%s and docstatus=1", v.name)[0]
        svc = frappe.db.sql("select coalesce(sum(cost),0) from `tabVehicle Service Log` where vehicle=%s and docstatus=1", v.name)[0][0] or 0
        ful = frappe.db.sql("select coalesce(sum(total_amount),0) from `tabFuel Log` where vehicle=%s and docstatus=1", v.name)[0][0] or 0
        tc, rev = flt(td[1]), flt(td[2])
        total = tc + svc + ful
        data.append({"vehicle":v.name,"vehicle_type":v.vehicle_type,"trips":td[0],
            "trip_costs":tc,"service_costs":svc,"fuel_costs":ful,"total":total,"revenue":rev,"net":rev-total})
    return cols, data
