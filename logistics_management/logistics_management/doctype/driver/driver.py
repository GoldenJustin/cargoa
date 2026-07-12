# -*- coding: utf-8 -*-
"""
Driver master.

A driver can be:
  * an Own Employee  -> linked to an Employee record (salary via Payroll)
  * a Hired Contractor -> linked to a Supplier (paid via Purchase / Payment chain)

This is what lets the same "Driver" field work for both company staff and
outsourced / sub-contracted drivers.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, add_to_date


class Driver(Document):
	def validate(self):
		if self.driver_type == "Own Employee":
			if not self.linked_employee:
				frappe.throw(_("Please link an Employee for an Own Employee driver."))
		elif self.driver_type == "Hired Contractor":
			if not self.linked_supplier:
				frappe.msgprint(
					_("Tip: link a Supplier so the hired driver's allowances can be paid through accounting."),
					indicator="orange",
				)

		if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
			frappe.msgprint(_("Warning: this driver's license has expired."), indicator="red")
