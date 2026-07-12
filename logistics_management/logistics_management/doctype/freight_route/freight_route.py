# -*- coding: utf-8 -*-
"""
Freight Route - master definition of a standard journey.

Acts as the benchmark against which every trip is measured: distance,
expected fuel, and expected driver allowance. Used to detect fuel theft
and excessive allowance claims.
"""
import frappe
from frappe import _
from frappe.model.document import Document


class FreightRoute(Document):
	def validate(self):
		if self.origin and self.destination and self.origin.strip().lower() == self.destination.strip().lower():
			frappe.throw(_("Origin and Destination cannot be the same."))
		if self.trip_type == "Round Trip" and self.standard_fuel_allocation:
			frappe.msgprint(
				_("Note: Standard Fuel Allocation is recorded for the whole {0} journey.")
				.format(self.trip_type),
				indicator="blue",
			)
