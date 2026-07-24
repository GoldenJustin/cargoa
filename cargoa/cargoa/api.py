# -*- coding: utf-8 -*-
"""Cargoa Accounting Engine."""
import frappe
from frappe import _
from frappe.utils import flt, nowdate

def _resolve(trip_doc):
    settings = frappe.get_doc("Cargoa Settings")
    company = trip_doc.company or settings.company
    if not company: company = frappe.db.get_single_value("Global Defaults","default_company")
    if not company: return settings, None, None, None
    c = frappe.get_cached_doc("Company", company)
    cc = trip_doc.cost_center or settings.default_cost_center or getattr(c,"cost_center",None)
    return settings, company, cc, c

def _auto_submit(settings, doc):
    if settings.get("auto_submit_accounting") and doc.docstatus==0:
        try: doc.submit()
        except Exception: frappe.log_error(title="Cargoa auto-submit "+doc.doctype)

def _create_si(trip_doc):
    if trip_doc.sales_invoice or not trip_doc.customer or flt(trip_doc.total_revenue)<=0: return None
    settings,company,cc,c = _resolve(trip_doc)
    if not company: return None
    si = frappe.new_doc("Sales Invoice")
    si.customer=trip_doc.customer; si.company=company; si.posting_date=nowdate(); si.due_date=nowdate()
    si.cost_center=cc; si.set("freight_trip", trip_doc.name)
    si.append("items",{"item_code":settings.freight_income_item or "Freight Charges","qty":1,
        "rate":flt(trip_doc.total_revenue),
        "income_account":settings.freight_income_account or getattr(c,"default_income_account",None),
        "cost_center":cc,"description":_("Freight for trip {0}").format(trip_doc.name)})
    si.set_missing_values()
    try: si.run_method("calculate_taxes_and_totals")
    except Exception: pass
    si.insert(ignore_permissions=True)
    _auto_submit(settings, si)
    frappe.db.set_value("Freight Trip", trip_doc.name, "sales_invoice", si.name)
    return si.name

def _create_pi(trip_doc):
    if trip_doc.purchase_invoice or not trip_doc.prime_mover: return None
    v = frappe.get_doc("Transport Vehicle", trip_doc.prime_mover)
    if v.ownership_type!="Hired" or not v.linked_supplier or flt(trip_doc.truck_hire_rate)<=0: return None
    settings,company,cc,c = _resolve(trip_doc)
    if not company: return None
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier=v.linked_supplier; pi.company=company; pi.posting_date=nowdate(); pi.cost_center=cc
    pi.set("freight_trip", trip_doc.name)
    pi.append("items",{"item_code":settings.truck_hire_item or "Truck Hire","qty":1,
        "rate":flt(trip_doc.truck_hire_rate),
        "expense_account":settings.truck_hire_account or getattr(c,"default_expense_account",None),
        "cost_center":cc,"description":_("Hire of {0} for trip {1}").format(trip_doc.prime_mover, trip_doc.name)})
    pi.set_missing_values()
    pi.insert(ignore_permissions=True)
    _auto_submit(settings, pi)
    frappe.db.set_value("Freight Trip", trip_doc.name, "purchase_invoice", pi.name)
    return pi.name

def _create_pe_driver(trip_doc):
    if trip_doc.driver_payment or not trip_doc.driver: return None
    d = frappe.get_doc("Driver", trip_doc.driver)
    if d.driver_type!="Hired Contractor" or not d.linked_supplier or flt(trip_doc.total_allowances)<=0: return None
    settings,company,cc,c = _resolve(trip_doc)
    if not company: return None
    pf = settings.default_bank_account or settings.default_cash_account or getattr(c,"default_bank_account",None) or getattr(c,"default_cash_account",None)
    if not pf: return None
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type="Pay"; pe.party_type="Supplier"; pe.party=d.linked_supplier; pe.company=company
    pe.posting_date=nowdate(); pe.paid_from=pf; pe.paid_amount=flt(trip_doc.total_allowances)
    pe.received_amount=flt(trip_doc.total_allowances); pe.cost_center=cc
    pe.set("freight_trip", trip_doc.name); pe.remark=_("Driver allowance for trip {0}").format(trip_doc.name)
    pe.setup_party_account_field(); pe.set_missing_values()
    pe.insert(ignore_permissions=True)
    _auto_submit(settings, pe)
    frappe.db.set_value("Freight Trip", trip_doc.name, "driver_payment", pe.name)
    return pe.name

def auto_create_accounting(trip_name):
    results = {"sales_invoice":None,"purchase_invoice":None,"driver_payment":None}
    try:
        trip_doc = frappe.get_doc("Freight Trip", trip_name)
        results["sales_invoice"]=_create_si(trip_doc)
        results["purchase_invoice"]=_create_pi(trip_doc)
        results["driver_payment"]=_create_pe_driver(trip_doc)
        created=[k for k,v in results.items() if v]
        if created: frappe.msgprint(_("Accounting created: {0}").format(", ".join(created)), indicator="green")
    except Exception: frappe.log_error(title="Cargoa auto_accounting "+str(trip_name))
    return results

@frappe.whitelist()
def create_sales_invoice(trip):
    td = frappe.get_doc("Freight Trip", trip)
    if td.sales_invoice: frappe.throw(_("Sales Invoice already exists."))
    if not td.customer: frappe.throw(_("Set a Customer first."))
    name=_create_si(td)
    if not name: frappe.throw(_("Could not create SI. Check Cargoa Settings."))
    return name

@frappe.whitelist()
def create_truck_hire_invoice(trip):
    name=_create_pi(frappe.get_doc("Freight Trip", trip))
    if not name: frappe.throw(_("Could not create. Truck must be Hired with Supplier and rate set."))
    return name

@frappe.whitelist()
def pay_driver(trip):
    name=_create_pe_driver(frappe.get_doc("Freight Trip", trip))
    if not name: frappe.throw(_("Could not create. Driver must be Hired Contractor with Supplier."))
    return name

@frappe.whitelist()
def receive_customer_payment(trip, amount=None):
    td = frappe.get_doc("Freight Trip", trip)
    if not td.customer or not td.sales_invoice: frappe.throw(_("Create Sales Invoice first."))
    settings,company,cc,c = _resolve(td)
    rt = settings.default_bank_account or settings.default_cash_account or getattr(c,"default_bank_account",None)
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type="Receive"; pe.party_type="Customer"; pe.party=td.customer; pe.company=company
    pe.posting_date=nowdate(); pe.paid_to=rt; pe.paid_amount=flt(amount) if amount else flt(td.total_revenue)
    pe.received_amount=pe.paid_amount; pe.cost_center=cc; pe.set("freight_trip", trip)
    pe.setup_party_account_field(); pe.set_paid_amount(); pe.set_missing_values()
    pe.append("references",{"reference_doctype":"Sales Invoice","reference_name":td.sales_invoice,
        "total_amount":flt(td.total_revenue),"allocated_amount":pe.paid_amount})
    pe.insert(ignore_permissions=True)
    return pe.name

def on_voucher_cancel(doc, method=None):
    try:
        trip = doc.get("freight_trip") if hasattr(doc,"get") else None
        if trip and frappe.db.exists("Freight Trip", trip):
            from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
            update_trip_costs(trip)
    except Exception: pass
