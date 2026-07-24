# -*- coding: utf-8 -*-
from frappe.model.document import Document
class VehicleServiceLog(Document):
    def on_submit(self):
        if self.vehicle:
            try:
                u = {}
                if self.next_service_date: u["next_service_date"] = self.next_service_date
                if self.odometer_reading: u["odometer_reading"] = self.odometer_reading
                if u: frappe.db.set_value("Transport Vehicle", self.vehicle, u)
            except Exception: pass
