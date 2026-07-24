# -*- coding: utf-8 -*-
"""Scheduled tasks."""
import frappe
from frappe.utils import today, add_days

def daily_maintenance():
    try:
        frappe.db.sql("select name from `tabTransport Vehicle` where is_active=1 and "
            "((insurance_expiry is not null and insurance_expiry<=%s) or "
            "(license_expiry is not null and license_expiry<=%s))",
            (add_days(today(),30), add_days(today(),30)))
    except Exception: pass
