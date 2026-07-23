# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document

class ShipmentTracking(Document):
	def validate(self):
		# Mark previous tracking events as not-latest when a new one is added
		if self.freight_trip:
			frappe.db.sql("""
				update `tabShipment Tracking`
				set is_latest = 0
				where freight_trip = %s and name != %s
			""", (self.freight_trip, self.name or "___"))

		# Sync trip status
		if self.freight_trip and self.status:
			try:
				status_map = {
					"Booked": "Scheduled", "Picked Up": "In Transit",
					"Departed Origin": "In Transit", "In Transit": "In Transit",
					"At Hub": "In Transit", "Out for Delivery": "In Transit",
					"Delivered": "Completed", "Exception": "In Transit",
					"Returned": "In Transit",
				}
				trip_status = status_map.get(self.status)
				if trip_status:
					frappe.db.set_value("Freight Trip", self.freight_trip, "trip_status", trip_status)
			except Exception:
				pass

	def on_update(self):
		"""Send customer notification if enabled."""
		try:
			settings = frappe.get_doc("Cargoa Settings")
			if not settings.get("notify_customer"):
				return
			if self.status == "Delivered":
				self._send_notification("Shipment Delivered")
			elif self.status == "Departed Origin":
				self._send_notification("Shipment Dispatched")
		except Exception:
			pass

	def _send_notification(self, notif_name):
		try:
			notif = frappe.get_doc("Notification", notif_name)
			if notif.enabled:
				notif_eval = notif
		except Exception:
			pass
