# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document

class FreightRoute(Document):
	def validate(self):
		if self.origin and self.destination and self.origin.strip().lower() == self.destination.strip().lower():
			frappe.throw(_("Origin and Destination cannot be the same."))
