# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
class Waybill(Document):
    def validate(self):
        if self.waybill_status=="Delivered" and not self.pod_attachment:
            frappe.throw(_("Delivered waybill needs POD."))
    def before_submit(self):
        if self.pod_attachment and self.waybill_status in ("Draft","Loaded","In Transit"):
            self.waybill_status="Delivered"
    def on_update_after_submit(self):
        if self.freight_trip:
            try:
                from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
                update_trip_costs(self.freight_trip)
            except Exception: pass
