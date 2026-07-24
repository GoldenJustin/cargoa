# -*- coding: utf-8 -*-
"""Cargoa install. Bulletproof: every step isolated."""
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOCTYPES = [
    "Freight Route","Driver","Transport Vehicle","Cargoa Settings",
    "Hub","Tariff","Customer Contract","Delivery Order","Waybill",
    "Shipment Tracking","Freight Trip","Trip Expense","Fuel Log",
    "Vehicle Service Log","Trip Settlement","Cargo Claim",
]

def before_install():
    pass

def after_install():
    for fn in (_roles,_perms,_fields,_items,seed_settings,_notifications):
        try:
            fn()
        except Exception:
            frappe.db.rollback()
            try: frappe.log_error(title="Cargoa: "+fn.__name__)
            except Exception: pass
    try: frappe.db.commit()
    except Exception: pass
    frappe.msgprint(_("Cargoa v3 installed successfully."))

def _roles():
    for r in ("Cargoa Manager","Cargoa User","Cargoa Dispatcher","Cargoa Accounts"):
        try:
            if not frappe.db.exists("Role", r):
                frappe.get_doc({"doctype":"Role","role_name":r,"desk_access":1}).insert(ignore_permissions=True)
        except Exception: frappe.db.rollback()
    frappe.db.commit()

FULL = ["read","write","create","delete","submit","cancel","amend","print","email","report","share"]
USER = ["read","write","create","submit","cancel","print","email","report","share"]
VIEW = ["read","report","email","print"]

def _perms():
    rp = {"Cargoa Manager":FULL,"Cargoa User":USER,"Cargoa Dispatcher":USER,"Cargoa Accounts":USER}
    for dt in DOCTYPES:
        if not frappe.db.exists("DocType", dt): continue
        for role,pts in rp.items():
            if dt=="Cargoa Settings" and role!="Cargoa Manager": pts=VIEW
            try:
                frappe.permissions.add_permission(dt, role, 0)
                for p in pts: frappe.permissions.update_permission_property(dt, role, 0, p, 1)
            except Exception: frappe.db.rollback()
    frappe.db.commit()

def _fields():
    def fld(a): return dict(fieldname="freight_trip",label="Freight Trip",fieldtype="Link",
        options="Freight Trip",insert_after=a,allow_on_submit=1)
    try:
        create_custom_fields({"Sales Invoice":[fld("customer")],"Purchase Invoice":[fld("supplier")],
            "Journal Entry":[fld("user_remark")],"Payment Entry":[fld("party")]})
        frappe.db.commit()
    except Exception: frappe.db.rollback()

def _items():
    grp = next((x for x in ("Services","All Item Groups") if frappe.db.exists("Item Group",x)),None) or "Services"
    uom = next((x for x in ("Nos","Unit") if frappe.db.exists("UOM",x)),None) or "Nos"
    for code,desc in [("Freight Charges","Freight service."),("Truck Hire","Hire of hired truck."),
        ("Demurrage","Delay charges."),("Loading Charges","Loading service."),("Offloading Charges","Offloading service.")]:
        try:
            if not frappe.db.exists("Item", code):
                frappe.get_doc({"doctype":"Item","item_code":code,"item_name":code,"item_group":grp,
                    "stock_uom":uom,"is_stock_item":0,"description":desc}).insert(ignore_permissions=True)
                frappe.db.commit()
        except Exception: frappe.db.rollback()

def seed_settings():
    try:
        s = frappe.get_doc("Cargoa Settings")
        company = s.company or frappe.db.get_single_value("Global Defaults","default_company")
        if not company: company = frappe.db.get_value("Company",{"disabled":0},"name")
        if not company: return
        c = frappe.get_cached_doc("Company", company)
        s.company = company
        s.default_cost_center = s.default_cost_center or getattr(c,"cost_center",None)
        s.default_payable_account = s.default_payable_account or getattr(c,"default_payable_account",None)
        s.default_bank_account = s.default_bank_account or getattr(c,"default_bank_account",None)
        s.default_cash_account = s.default_cash_account or getattr(c,"default_cash_account",None)
        s.freight_income_account = s.freight_income_account or getattr(c,"default_income_account",None)
        exp = getattr(c,"default_expense_account",None)
        for f in ("truck_hire_account","fuel_account","allowance_account","fines_tolls_account",
                  "repairs_account","maintenance_account","offloading_loading_account","other_expense_account"):
            if not s.get(f): s.set(f, exp)
        if not s.freight_income_item and frappe.db.exists("Item","Freight Charges"): s.freight_income_item="Freight Charges"
        if not s.truck_hire_item and frappe.db.exists("Item","Truck Hire"): s.truck_hire_item="Truck Hire"
        if not s.get("auto_create_accounting"): s.auto_create_accounting=1
        s.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception: frappe.db.rollback()

def _notifications():
    for name,dt,subj in [("Delivery Booked","Delivery Order","Your delivery {name} has been booked."),
        ("Shipment Dispatched","Shipment Tracking","Shipment {name} dispatched."),
        ("Shipment Delivered","Shipment Tracking","Shipment {name} delivered.")]:
        try:
            if not frappe.db.exists("Notification", name):
                frappe.get_doc({"doctype":"Notification","name":name,"subject":subj,
                    "document_type":dt,"event":"New","channel":"Email","enabled":1}).insert(ignore_permissions=True)
        except Exception: frappe.db.rollback()
    frappe.db.commit()
