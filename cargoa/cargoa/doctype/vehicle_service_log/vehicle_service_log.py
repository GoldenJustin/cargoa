# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class VehicleServiceLog(Document):
	def on_submit(self):
		# Update vehicle's next service info and odometer
		if self.vehicle:
			try:
				updates = {}
				if self.next_service_date:
					updates["next_service_date"] = self.next_service_date
				if self.odometer_reading:
					updates["odometer_reading"] = self.odometer_reading
				if updates:
					frappe.db.set_value("Transport Vehicle", self.vehicle, updates)
			except Exception:
				pass
