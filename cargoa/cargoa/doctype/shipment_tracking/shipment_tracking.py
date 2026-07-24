# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class ShipmentTracking(Document):
    def validate(self):
        if self.freight_trip:
            frappe.db.sql("update `tabShipment Tracking` set is_latest=0 where freight_trip=%s and name!=%s",
                (self.freight_trip, self.name or "___"))
        status_map = {"Booked":"Scheduled","Picked Up":"In Transit","Departed Origin":"In Transit",
            "In Transit":"In Transit","At Hub":"In Transit","Out for Delivery":"In Transit",
            "Delivered":"Completed","Exception":"In Transit","Returned":"In Transit"}
        if self.freight_trip and self.status and self.status in status_map:
            try: frappe.db.set_value("Freight Trip", self.freight_trip, "trip_status", status_map[self.status])
            except Exception: pass
