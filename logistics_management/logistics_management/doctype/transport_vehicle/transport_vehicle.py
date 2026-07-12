# -*- coding: utf-8 -*-
"""
Transport Vehicle master.

Handles BOTH prime movers and trailers (selected via Vehicle Type) and BOTH
company-owned and hired trucks (Ownership Type). A hired truck links to its
owner as a Supplier so hire is settled through the accounting chain.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class TransportVehicle(Document):
	def validate(self):
		if self.ownership_type == "Hired" and not self.linked_supplier:
			frappe.throw(_("A hired vehicle must have an Owner (Supplier) linked."))

		for field in ("insurance_expiry", "license_expiry"):
			if self.get(field) and getdate(self.get(field)) < getdate(today()):
				frappe.msgprint(
					_("Warning: {0} has expired for this vehicle.").format(
						self.meta.get_label(field)
					),
					indicator="red",
				)
