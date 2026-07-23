# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document

class DeliveryOrder(Document):
	def validate(self):
		# Auto-compute estimated cost from tariff
		if self.route and self.weight and not self.estimated_cost:
			try:
				from cargoa.cargoa.utils import compute_route_tariff
				tariff_name, amount = compute_route_tariff(self.route, self.weight)
				if tariff_name:
					self.tariff_applied = tariff_name
					self.estimated_cost = amount
			except Exception:
				pass

	def before_submit(self):
		if self.status == "Draft":
			self.status = "Confirmed"
