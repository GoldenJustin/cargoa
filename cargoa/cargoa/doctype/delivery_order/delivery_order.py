# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class DeliveryOrder(Document):
    def validate(self):
        if self.route and self.weight and not self.estimated_cost:
            try:
                from cargoa.cargoa.utils import compute_route_tariff
                tn, amt = compute_route_tariff(self.route, self.weight)
                if tn: self.tariff_applied = tn; self.estimated_cost = amt
            except Exception: pass
    def before_submit(self):
        if self.status=="Draft": self.status="Confirmed"
