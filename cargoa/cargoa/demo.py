# -*- coding: utf-8 -*-
"""Demo data creator. Run: from cargoa.cargoa.demo import create_demo_data; create_demo_data()"""
import frappe
from frappe.utils import flt, today, now

def create_demo_data():
    company = frappe.db.get_single_value("Global Defaults","default_company")
    if not company: company = frappe.db.get_value("Company",{"disabled":0},"name")
    if not company: frappe.throw("No company found.")
    _routes(); emp1=_emp(company,"Juma Mushi"); emp2=_emp(company,"Peter John")
    _drivers(emp1,emp2); _vehicles(); _customers(); _tariffs()
    wb1=_waybill(company,"Twiga Cement","Dar es Salaam","Mwanza","Cement",30)
    wb2=_waybill(company,"KNCJ Coca Cola","Dar es Salaam","Arusha","Beverages",25)
    t1=_trip(company,"Dar es Salaam - Mwanza",wb1,"Juma Mushi","T 123 ABC",120000)
    t2=_trip(company,"Dar es Salaam - Arusha",wb2,"Hassan Ali","T 456 DEF",100000)
    _expenses(company,t1); _tracking(company,t1); _tracking(company,t2)
    frappe.db.commit()
    frappe.msgprint("✅ Demo data created!", indicator="green")

def _emp(company, name):
    emp = frappe.db.get_value("Employee", {"employee_name": name})
    if emp: return emp
    try:
        return frappe.get_doc({"doctype":"Employee","employee_name":name,"company":company,
            "status":"Active","gender":"Male"}).insert(ignore_permissions=True).name
    except Exception:
        frappe.db.rollback()
        return frappe.db.get_value("Employee", {"company": company})

def _routes():
    for name,o,d,dist,fuel,allow in [("Dar es Salaam - Mwanza","Dar es Salaam","Mwanza",1180,320,150000),
        ("Dar es Salaam - Arusha","Dar es Salaam","Arusha",640,180,80000)]:
        if not frappe.db.exists("Freight Route", name):
            try: frappe.get_doc({"doctype":"Freight Route","route_name":name,"origin":o,
                "destination":d,"total_distance_km":dist,"trip_type":"One-Way",
                "standard_fuel_allocation":fuel,"standard_driver_allowance":allow,
                "estimated_duration_hours":round(dist/60,1)}).insert(ignore_permissions=True)
            except Exception: frappe.db.rollback()

def _drivers(emp1,emp2):
    if not frappe.db.exists("Supplier","Demo Driver Co"):
        try: frappe.get_doc({"doctype":"Supplier","supplier_name":"Demo Driver Co",
            "supplier_group":"All Supplier Groups"}).insert(ignore_permissions=True)
        except Exception: frappe.db.rollback()
    for name,dt,emp,sup in [("Juma Mushi","Own Employee",emp1,None),
        ("Hassan Ali","Hired Contractor",None,"Demo Driver Co"),
        ("Peter John","Own Employee",emp2,None)]:
        if not frappe.db.exists("Driver", name):
            try:
                doc = frappe.get_doc({"doctype":"Driver","driver_name":name,"driver_type":dt,
                    "phone":"+255 700 000 000","license_number":"DL-"+name.replace(" ","")[:6].upper()})
                if emp: doc.linked_employee=emp
                if sup: doc.linked_supplier=sup
                doc.insert(ignore_permissions=True)
            except Exception: frappe.db.rollback()

def _vehicles():
    for reg,vt,own,sup,mk,md in [("T 123 ABC","Prime Mover","Owned",None,"Scania","R450"),
        ("T 456 DEF","Prime Mover","Hired","Demo Driver Co","Mercedes","Actros"),
        ("TR 789 GHI","Trailer","Owned",None,"Schmitz","Curtain")]:
        if not frappe.db.exists("Transport Vehicle", reg):
            try:
                doc = frappe.get_doc({"doctype":"Transport Vehicle","registration_number":reg,
                    "vehicle_type":vt,"ownership_type":own,"make":mk,"model":md,
                    "fuel_type":"Diesel","capacity":30,"average_fuel_efficiency":3.5})
                if sup: doc.linked_supplier=sup
                doc.insert(ignore_permissions=True)
            except Exception: frappe.db.rollback()

def _customers():
    for name in ["Twiga Cement","KNCJ Coca Cola"]:
        if not frappe.db.exists("Customer", name):
            try: frappe.get_doc({"doctype":"Customer","customer_name":name,
                "customer_group":"All Customer Groups","territory":"All Territories"}).insert(ignore_permissions=True)
            except Exception: frappe.db.rollback()

def _tariffs():
    if not frappe.db.exists("Tariff","Standard Per Ton"):
        try: frappe.get_doc({"doctype":"Tariff","tariff_name":"Standard Per Ton",
            "rate_type":"Per Ton","base_rate":100000,"is_active":1}).insert(ignore_permissions=True)
        except Exception: frappe.db.rollback()

def _waybill(company,cust,load,offload,cargo,wt):
    ex = frappe.db.get_value("Waybill", {"customer":cust})
    if ex: return ex
    try:
        wb = frappe.get_doc({"doctype":"Waybill","company":company,"waybill_date":today(),
            "customer":cust,"cargo_description":cargo,"weight_quantity":wt,"uom":"Ton",
            "loading_point":load,"offloading_point":offload,"waybill_status":"Loaded"})
        wb.insert(ignore_permissions=True); wb.submit(); return wb.name
    except Exception: frappe.db.rollback()
    return frappe.db.get_value("Waybill", {"customer":cust})

def _trip(company,route,wb,driver,vehicle,rate):
    if not wb: return None
    try:
        t = frappe.get_doc({"doctype":"Freight Trip","company":company,"trip_date":today(),
            "route":route,"prime_mover":vehicle,"driver":driver,"waybill":wb,"agreed_rate":rate})
        t.insert(ignore_permissions=True); return t.name
    except Exception: frappe.db.rollback()
    return None

def _expenses(company,trip):
    if not trip: return
    for cat,qty,amt,pb in [("Fuel",250,280000,"Company"),("Driver Allowance (Posho)",0,150000,"Driver Pocket"),
        ("Weighbridge Fine",0,30000,"Company"),("Toll Gate",0,5000,"Company"),("En-route Repair",0,120000,"Company")]:
        try:
            e = frappe.get_doc({"doctype":"Trip Expense","company":company,"expense_date":today(),
                "freight_trip":trip,"expense_category":cat,"quantity":qty,"amount":amt,"paid_by":pb,
                "description":"Demo: "+cat})
            e.insert(ignore_permissions=True); e.submit()
        except Exception: frappe.db.rollback()

def _tracking(company,trip):
    if not trip: return
    for status,loc in [("Booked","Dar es Salaam"),("Departed Origin","Morogoro"),("In Transit","Dodoma")]:
        try:
            tr = frappe.get_doc({"doctype":"Shipment Tracking","company":company,
                "freight_trip":trip,"status":status,"location":loc,"is_customer_visible":1})
            tr.insert(ignore_permissions=True); tr.submit()
        except Exception: frappe.db.rollback()
