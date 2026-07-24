# -*- coding: utf-8 -*-
"""Shared utility functions."""
import frappe
from frappe.utils import flt

def get_settings():
    return frappe.get_doc("Cargoa Settings")

def compute_route_tariff(route, weight):
    amount = 0; tariff_name = None
    tariffs = frappe.db.sql("select name, rate_type, base_rate, min_charge from `tabTariff` "
        "where (route=%s or route is null) and is_active=1 order by (case when route=%s then 0 else 1 end), valid_from desc limit 1",
        (route or "", route or ""), as_dict=True)
    if tariffs:
        t = tariffs[0]; tariff_name = t["name"]
        amount = flt(weight)*flt(t["base_rate"]) if t["rate_type"]=="Per Ton" else flt(t["base_rate"])
        if flt(t["min_charge"])>amount: amount = flt(t["min_charge"])
    return tariff_name, amount
