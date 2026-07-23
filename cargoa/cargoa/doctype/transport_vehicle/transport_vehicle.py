# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

class TransportVehicle(Document):
	def validate(self):
		if self.ownership_type == "Hired" and not self.linked_supplier:
			frappe.throw(_("A hired vehicle must have an Owner (Supplier) linked."))
