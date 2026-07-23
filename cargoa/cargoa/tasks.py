# -*- coding: utf-8 -*-
"""Scheduled tasks for Cargoa — runs daily via scheduler_events."""
import frappe
from frappe.utils import today, add_days, flt


def daily_maintenance():
	"""Daily checks: expiring licenses, vehicle service due, contract expiry alerts."""
	try:
		# Vehicle compliance expiring in 30 days
		for v in frappe.db.sql("""
			select name, registration_number, insurance_expiry, license_expiry
			from `tabTransport Vehicle`
			where is_active = 1 and (
				(insurance_expiry is not null and insurance_expiry <= %s) or
				(license_expiry is not null and license_expiry <= %s))
		""", (add_days(today(), 30), add_days(today(), 30)), as_dict=True):
			frappe.logger().info("Cargoa: vehicle %s has expiring compliance" % v["name"])
	except Exception:
		pass

	try:
		# Contracts expiring in 30 days
		for ct in frappe.db.sql("""
			select name, customer from `tabCustomer Contract`
			where status = 'Active' and end_date is not null and end_date <= %s
		""", (add_days(today(), 30)), as_dict=True):
			frappe.logger().info("Cargoa: contract %s for %s expiring soon" % (ct["name"], ct["customer"]))
	except Exception:
		pass
