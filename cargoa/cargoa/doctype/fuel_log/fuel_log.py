# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FuelLog(Document):
	def validate(self):
		self.total_amount = flt(self.liters) * flt(self.rate_per_liter)
		# Update vehicle odometer if higher
		if self.vehicle and self.odometer_reading:
			try:
				current = frappe.db.get_value("Transport Vehicle", self.vehicle, "odometer_reading") or 0
				if self.odometer_reading > current:
					frappe.db.set_value("Transport Vehicle", self.vehicle, "odometer_reading", self.odometer_reading)
			except Exception:
				pass

	def on_submit(self):
		# Optionally create a Trip Expense for this fuel log
		if self.freight_trip:
			try:
				from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
				update_trip_costs(self.freight_trip)
			except Exception:
				pass
