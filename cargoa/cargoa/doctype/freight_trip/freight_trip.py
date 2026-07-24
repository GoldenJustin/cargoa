# -*- coding: utf-8 -*-
"""Freight Trip — THE HUB."""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

CAT = {"Fuel":"total_fuel_cost","Driver Allowance (Posho)":"total_allowances",
    "Weighbridge Fine":"total_fines_tolls","Toll Gate":"total_fines_tolls",
    "En-route Repair":"total_repairs","Offloading Fee":"total_offloading_loading",
    "Loading Fee":"total_offloading_loading","Truck Hire":"total_truck_hire","Other":"total_other"}
BUCKETS = list(set(CAT.values()))
ROLLED = BUCKETS + ["total_trip_cost","trip_profit","profit_margin","total_fuel_liters","fuel_variance_liters"]

class FreightTrip(Document):
    def validate(self):
        self._rev(); self._costs(); self._bench()
    def before_submit(self):
        s = frappe.get_doc("Cargoa Settings")
        if not self.customer: frappe.throw(_("Customer required."))
        if not s.get("allow_zero_revenue_trips") and flt(self.total_revenue)<=0:
            frappe.throw(_("Revenue must be > 0."))
        self._costs()
        if self.trip_status in ("Draft","Scheduled","In Transit"): self.trip_status="Completed"
    def on_submit(self):
        s = frappe.get_doc("Cargoa Settings")
        if not s.get("auto_create_accounting",1): return
        try:
            from cargoa.cargoa.api import auto_create_accounting
            auto_create_accounting(self.name)
        except Exception: frappe.log_error(title="Cargoa auto "+str(self.name))
    def on_cancel(self): self.db_set("trip_status","Cancelled")
    def _rev(self):
        if not self.is_flat_rate: self.total_revenue = flt(self.cargo_weight)*flt(self.agreed_rate)
    def _costs(self):
        bd = breakdown(self.name)
        for f in ROLLED: self.set(f, flt(bd.get(f,0)))
        self.trip_profit = flt(self.total_revenue)-flt(self.total_trip_cost)
        self.profit_margin = (self.trip_profit/flt(self.total_revenue)*100.0) if flt(self.total_revenue) else 0
        self.fuel_variance_liters = (flt(self.total_fuel_liters)-flt(self.standard_fuel_allocation)) if flt(self.standard_fuel_allocation) else 0
    def _bench(self):
        s = frappe.get_doc("Cargoa Settings")
        if flt(self.standard_fuel_allocation) and flt(self.total_fuel_liters)>flt(self.standard_fuel_allocation):
            frappe.msgprint(_("Warning: fuel ({0}L) exceeds standard ({1}L).").format(self.total_fuel_liters,self.standard_fuel_allocation),indicator="orange")
        if s.get("warn_negative_margin") and flt(self.profit_margin)<0:
            frappe.msgprint(_("Warning: negative margin ({0}%).").format(self.profit_margin),indicator="red")

def breakdown(trip):
    rows = frappe.db.sql("select expense_category, sum(amount) amt, sum(quantity) qty from `tabTrip Expense` where freight_trip=%s and docstatus=1 group by expense_category", trip, as_dict=True)
    out = {f:0.0 for f in ROLLED}
    for r in rows:
        b = CAT.get(r.expense_category,"total_other"); out[b] += flt(r.amt)
        if r.expense_category=="Fuel": out["total_fuel_liters"] += flt(r.qty or 0)
    out["total_trip_cost"] = sum(out[f] for f in BUCKETS)
    return out

def update_trip_costs(trip):
    if not trip or not frappe.db.exists("Freight Trip", trip): return
    try:
        t = frappe.get_doc("Freight Trip", trip); t._costs()
        frappe.db.set_value("Freight Trip", trip, {f: t.get(f) for f in ROLLED}, update_modified=False)
    except Exception: frappe.log_error(title="Cargoa update_costs "+str(trip))
