# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
class FuelLog(Document):
    def validate(self):
        self.total_amount = flt(self.liters)*flt(self.rate_per_liter)
        if self.vehicle and self.odometer_reading:
            try:
                cur = frappe.db.get_value("Transport Vehicle", self.vehicle, "odometer_reading") or 0
                if self.odometer_reading > cur:
                    frappe.db.set_value("Transport Vehicle", self.vehicle, "odometer_reading", self.odometer_reading)
            except Exception: pass
