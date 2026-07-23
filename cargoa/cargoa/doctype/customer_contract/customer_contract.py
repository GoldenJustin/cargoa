# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, getdate

class CustomerContract(Document):
	def validate(self):
		if self.end_date and self.start_date and getdate(self.end_date) < getdate(self.start_date):
			frappe.throw(_("End Date cannot be before Start Date."))

	def on_update(self):
		"""Update stats: count trips and sum revenue for this customer."""
		if not self.customer:
			return
		try:
			data = frappe.db.sql("""
				select count(*) as cnt, coalesce(sum(total_revenue),0) as rev
				from `tabFreight Trip` where customer = %s and docstatus = 1
			""", self.customer, as_dict=True)
			if data:
				self.db_set("total_trips", data[0]["cnt"] or 0)
				self.db_set("total_revenue", flt(data[0]["rev"]))
		except Exception:
			pass
