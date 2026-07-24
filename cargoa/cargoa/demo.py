# -*- coding: utf-8 -*-
"""
Cargoa Demo Data — creates a full realistic dataset for testing.

Run from bench console:
    from cargoa.cargoa.demo import create_demo_data
    create_demo_data()
"""
import frappe
from frappe.utils import flt, today, add_days, now, nowdate


def create_demo_data():
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		company = frappe.db.get_value("Company", {"disabled": 0}, "name")
	if not company:
		frappe.throw("No company found. Set up a company first.")

	_create_routes()
	emp1 = _get_or_create_employee(company, "Juma Mushi")
	emp2 = _get_or_create_employee(company, "Peter John")
	_create_drivers(emp1, emp2)
	_create_vehicles()
	_create_customers()
	_create_tariffs()
	wb1 = _create_waybill(company, "Twiga Cement", "Dar es Salaam", "Mwanza", "Cement", 30, "Ton")
	wb2 = _create_waybill(company, "KNCJ Coca Cola", "Dar es Salaam", "Arusha", "Beverages", 25, "Ton")
	trip1 = _create_trip(company, "Dar es Salaam - Mwanza", wb1, "Juma Mushi", "T 123 ABC", 120000)
	trip2 = _create_trip(company, "Dar es Salaam - Arusha", wb2, "Hassan Ali", "T 456 DEF", 100000)
	_create_expenses(company, trip1)
	_create_tracking(company, trip1)
	_create_tracking(company, trip2)
	frappe.db.commit()
	frappe.msgprint("✅ Demo data created! Check the Cargoa workspace for KPIs and charts.", indicator="green")


def _get_or_create_employee(company, name):
	"""Find an existing employee by name or create a minimal one."""
	emp = frappe.db.get_value("Employee", {"employee_name": name})
	if emp:
		return emp
	try:
		doc = frappe.get_doc({
			"doctype": "Employee", "employee_name": name,
			"company": company, "status": "Active",
			"gender": "Male",
		})
		doc.insert(ignore_permissions=True)
		return doc.name
	except Exception:
		frappe.db.rollback()
		# fallback: return any employee
		return frappe.db.get_value("Employee", {"company": company})


def _create_routes():
	routes = [
		("Dar es Salaam - Mwanza", "Dar es Salaam", "Mwanza", 1180, 320, 150000),
		("Dar es Salaam - Arusha", "Dar es Salaam", "Arusha", 640, 180, 80000),
	]
	for name, origin, dest, dist, fuel, allowance in routes:
		if not frappe.db.exists("Freight Route", name):
			frappe.get_doc({
				"doctype": "Freight Route", "route_name": name, "origin": origin,
				"destination": dest, "total_distance_km": dist, "trip_type": "One-Way",
				"standard_fuel_allocation": fuel, "standard_driver_allowance": allowance,
				"estimated_duration_hours": round(dist / 60, 1),
			}).insert(ignore_permissions=True)


def _create_drivers(emp1, emp2):
	suppliers = {
		"Hassan Ali": "Demo Driver Co",
	}
	for name, supp in suppliers.items():
		if not frappe.db.exists("Supplier", supp):
			try:
				frappe.get_doc({"doctype": "Supplier", "supplier_name": supp,
					"supplier_group": "All Supplier Groups"}).insert(ignore_permissions=True)
			except Exception:
				frappe.db.rollback()

	drivers = [
		("Juma Mushi", "Own Employee", emp1, None),
		("Hassan Ali", "Hired Contractor", None, "Demo Driver Co"),
		("Peter John", "Own Employee", emp2, None),
	]
	for name, dtype, emp, supp in drivers:
		if not frappe.db.exists("Driver", name):
			try:
				doc = frappe.get_doc({
					"doctype": "Driver", "driver_name": name, "driver_type": dtype,
					"phone": "+255 700 000 000",
					"license_number": "DL-" + name.replace(" ", "")[:6].upper(),
				})
				if emp:
					doc.linked_employee = emp
				if supp:
					doc.linked_supplier = supp
				doc.insert(ignore_permissions=True)
			except Exception:
				frappe.db.rollback()


def _create_vehicles():
	sup = "Demo Driver Co"
	vehicles = [
		("T 123 ABC", "Prime Mover", "Owned", None, "Scania", "R450"),
		("T 456 DEF", "Prime Mover", "Hired", sup, "Mercedes", "Actros"),
		("TR 789 GHI", "Trailer", "Owned", None, "Schmitz", "Curtain"),
	]
	for reg, vtype, ownership, supplier, make, model in vehicles:
		if not frappe.db.exists("Transport Vehicle", reg):
			try:
				doc = frappe.get_doc({
					"doctype": "Transport Vehicle", "registration_number": reg,
					"vehicle_type": vtype, "ownership_type": ownership,
					"make": make, "model": model, "fuel_type": "Diesel",
					"capacity": 30, "average_fuel_efficiency": 3.5,
				})
				if supplier:
					doc.linked_supplier = supplier
				doc.insert(ignore_permissions=True)
			except Exception:
				frappe.db.rollback()


def _create_customers():
	for name in ["Twiga Cement", "KNCJ Coca Cola"]:
		if not frappe.db.exists("Customer", name):
			try:
				frappe.get_doc({"doctype": "Customer", "customer_name": name,
					"customer_group": "All Customer Groups",
					"territory": "All Territories"}).insert(ignore_permissions=True)
			except Exception:
				frappe.db.rollback()


def _create_tariffs():
	if not frappe.db.exists("Tariff", "Standard Per Ton"):
		try:
			frappe.get_doc({"doctype": "Tariff", "tariff_name": "Standard Per Ton",
				"rate_type": "Per Ton", "base_rate": 100000, "is_active": 1,
			}).insert(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()


def _create_waybill(company, customer, loading, offloading, cargo, weight, uom):
	existing = frappe.db.get_value("Waybill", {"customer": customer})
	if existing:
		return existing
	try:
		wb = frappe.get_doc({
			"doctype": "Waybill", "company": company, "waybill_date": today(),
			"customer": customer, "cargo_description": cargo,
			"weight_quantity": weight, "uom": uom,
			"loading_point": loading, "offloading_point": offloading,
			"waybill_status": "Loaded",
		})
		wb.insert(ignore_permissions=True)
		wb.submit()
		return wb.name
	except Exception:
		frappe.db.rollback()
		return frappe.db.get_value("Waybill", {"customer": customer})


def _create_trip(company, route_name, waybill, driver, vehicle, rate):
	if not waybill:
		return None
	try:
		trip = frappe.get_doc({
			"doctype": "Freight Trip", "company": company,
			"trip_date": today(), "route": route_name,
			"prime_mover": vehicle, "driver": driver,
			"waybill": waybill, "agreed_rate": rate,
		})
		trip.insert(ignore_permissions=True)
		return trip.name
	except Exception:
		frappe.db.rollback()
		return None


def _create_expenses(company, trip_name):
	if not trip_name:
		return
	expenses = [
		("Fuel", 250, 280000, "Company"),
		("Driver Allowance (Posho)", 0, 150000, "Driver Pocket"),
		("Weighbridge Fine", 0, 30000, "Company"),
		("Toll Gate", 0, 5000, "Company"),
		("En-route Repair", 0, 120000, "Company"),
	]
	for category, qty, amount, paid_by in expenses:
		try:
			exp = frappe.get_doc({
				"doctype": "Trip Expense", "company": company,
				"expense_date": today(), "freight_trip": trip_name,
				"expense_category": category, "quantity": qty,
				"amount": amount, "paid_by": paid_by,
				"description": "Demo expense: " + category,
			})
			exp.insert(ignore_permissions=True)
			exp.submit()
		except Exception:
			frappe.db.rollback()


def _create_tracking(company, trip_name):
	if not trip_name:
		return
	for status, location in [("Booked", "Dar es Salaam"), ("Departed Origin", "Morogoro"), ("In Transit", "Dodoma")]:
		try:
			trk = frappe.get_doc({
				"doctype": "Shipment Tracking", "company": company,
				"freight_trip": trip_name, "status": status,
				"location": location, "is_customer_visible": 1,
			})
			trk.insert(ignore_permissions=True)
			trk.submit()
		except Exception:
			frappe.db.rollback()
