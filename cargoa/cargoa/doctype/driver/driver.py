# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

class Driver(Document):
	def validate(self):
		if self.driver_type == "Own Employee" and not self.linked_employee:
			frappe.msgprint(_("Tip: link an Employee for own-employee drivers (for Payroll)."), indicator="blue")
		if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
			frappe.msgprint(_("Warning: this driver's license has expired."), indicator="red")
