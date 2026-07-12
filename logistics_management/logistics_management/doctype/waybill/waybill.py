# -*- coding: utf-8 -*-
"""
Waybill (Consignment Note) - proof of cargo.

Submittable document describing what is being carried, for whom, from where
to where, and the proof of delivery (POD). The Weight here feeds the revenue
calculation on the Freight Trip.
"""
import frappe
from frappe import _
from frappe.model.document import Document


class Waybill(Document):
	def validate(self):
		if self.waybill_status == "Delivered" and not self.pod_attachment:
			frappe.throw(_("A Delivered waybill must have a POD Attachment."))

	def before_submit(self):
		# If POD has been received, promote the waybill to Delivered on submit.
		if self.pod_attachment and self.waybill_status in ("Draft", "Loaded", "In Transit"):
			self.waybill_status = "Delivered"

	def on_update_after_submit(self):
		# Keep the linked trip's revenue in sync if weight/rate inputs change.
		if self.freight_trip:
			from logistics_management.logistics_management.doctype.freight_trip.freight_trip import update_trip_costs
			update_trip_costs(self.freight_trip)
