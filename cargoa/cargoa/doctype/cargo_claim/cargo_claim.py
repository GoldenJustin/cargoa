# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CargoClaim(Document):
	def validate(self):
		if self.status == "Approved" and flt(self.approved_amount) <= 0:
			frappe.msgprint(_("Tip: set the Approved Amount for approved claims."), indicator="blue")
