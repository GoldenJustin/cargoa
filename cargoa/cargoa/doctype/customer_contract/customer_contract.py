# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
class CustomerContract(Document):
    def on_update(self):
        if not self.customer: return
        try:
            data = frappe.db.sql("select count(*) cnt, coalesce(sum(total_revenue),0) rev from `tabFreight Trip` where customer=%s and docstatus=1", self.customer)
            if data: self.db_set("total_trips", data[0][0] or 0); self.db_set("total_revenue", flt(data[0][1]))
        except Exception: pass
