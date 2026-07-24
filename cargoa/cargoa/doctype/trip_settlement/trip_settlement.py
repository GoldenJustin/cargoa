# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
TF = ["customer","route","driver","prime_mover","trip_date","total_revenue","total_trip_cost","sales_invoice","purchase_invoice","driver_payment"]
class TripSettlement(Document):
    def validate(self):
        self._fetch(); self._calc()
    def before_submit(self): self.status="Settled"
    def on_cancel(self): self.db_set("status","Draft")
    def _fetch(self):
        if not self.freight_trip: return
        d = frappe.db.get_value("Freight Trip", self.freight_trip, TF, as_dict=True)
        if d:
            for f in TF: self.set(f, d.get(f))
            if not self.company: self.company = frappe.db.get_value("Freight Trip", self.freight_trip, "company")
    def _calc(self):
        self.customer_balance = flt(self.total_revenue)-flt(self.amount_received)
        self.outstanding_costs = flt(self.total_trip_cost)-flt(self.amounts_paid_out)
        self.net_profit = flt(self.total_revenue)-flt(self.total_trip_cost)
        self.net_cash_position = flt(self.amount_received)-flt(self.amounts_paid_out)
