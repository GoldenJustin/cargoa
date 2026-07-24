# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
class TransportVehicle(Document):
    def validate(self):
        if self.ownership_type=="Hired" and not self.linked_supplier:
            frappe.throw(_("Hired vehicle must have an Owner linked."))
