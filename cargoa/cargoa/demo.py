# -*- coding: utf-8 -*-
"""
Cargoa Demo Data — creates a full realistic dataset for testing.

Run from bench console:
    from cargoa.cargoa.demo import create_demo_data
    create_demo_data()

Creates: 2 routes, 3 drivers, 3 vehicles, 2 customers, 1 tariff,
2 waybills, 2 freight trips, 5 trip expenses, 3 tracking events.
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
	_create_drivers()
	_create_vehicles()
	_create_customers()
	_create_tariffs(company)
	wb1 = _create_waybill(company, "Twiga Cement", "Dar es Salaam", "Mwanza", "Cement", 30, "Ton")
	wb2 = _create_waybill(company, "KNCJ Coca Cola", "Dar es Salaam", "Arusha", "Beverages", 25, "Ton")
	trip1 = _create_trip(company, "Dar es Salaam - Mwanza", wb1, "Juma Mushi", "T 123 ABC", 120000)
	trip2 = _create_trip(company, "Dar es Salaam - Arusha", wb2, "Hassan Ali", "T 456 DEF", 100000)
	_create_expenses(company, trip1)
	_create_tracking(company, trip1)
	_create_tracking(company, trip2)
	frappe.db.commit()
	frappe.msgprint("Demo data created successfully!", indicator="green")


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
				"estimated_duration_hours": dist / 60,
			}).insert(ignore_permissions=True)


def _create_drivers():
	drivers = [
		("Juma Mushi", "Own Employee", None),
		("Hassan Ali", "Hired Contractor", "Demo Driver Co"),
		("Peter John", "Own Employee", None),
	]
	for name, dtype, supplier in drivers:
		if not frappe.db.exists("Driver", name):
			doc = frappe.get_doc({
				"doctype": "Driver", "driver_name": name, "driver_type": dtype,
				"phone": "+255 700 000 000", "license_number": "DL-" + name[:3].upper(),
			})
			if supplier:
				if not frappe.db.exists("Supplier", supplier):
					frappe.get_doc({"doctype": "Supplier", "supplier_name": supplier,
						"supplier_group": "All Supplier Groups"}).insert(ignore_permissions=True)
				doc.linked_supplier = supplier
			doc.insert(ignore_permissions=True)


def _create_vehicles():
	vehicles = [
		("T 123 ABC", "Prime Mover", "Owned", None, "Scania", "R450"),
		("T 456 DEF", "Prime Mover", "Hired", "Demo Driver Co", "Mercedes", "Actros"),
		("TR 789 GHI", "Trailer", "Owned", None, "Schmitz", "Curtain"),
	]
	for reg, vtype, ownership, supplier, make, model in vehicles:
		if not frappe.db.exists("Transport Vehicle", reg):
			doc = frappe.get_doc({
				"doctype": "Transport Vehicle", "registration_number": reg,
				"vehicle_type": vtype, "ownership_type": ownership,
				"make": make, "model": model, "fuel_type": "Diesel",
				"capacity": 30, "average_fuel_efficiency": 3.5,
			})
			if supplier:
				doc.linked_supplier = supplier
			doc.insert(ignore_permissions=True)


def _create_customers():
	customers = ["Twiga Cement", "KNCJ Coca Cola"]
	for name in customers:
		if not frappe.db.exists("Customer", name):
			frappe.get_doc({"doctype": "Customer", "customer_name": name,
				"customer_group": "All Customer Groups",
				"territory": "All Territories"}).insert(ignore_permissions=True)


def _create_tariffs(company):
	if not frappe.db.exists("Tariff", "Standard Per Ton"):
		frappe.get_doc({
			"doctype": "Tariff", "tariff_name": "Standard Per Ton",
			"rate_type": "Per Ton", "base_rate": 100000, "is_active": 1,
		}).insert(ignore_permissions=True)


def _create_waybill(company, customer, loading, offloading, cargo, weight, uom):
	name = customer.split()[0] + "-" + today()
	if not frappe.db.exists("Waybill", {"customer": customer}):
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
	return frappe.db.get_value("Waybill", {"customer": customer}, "name")


def _create_trip(company, route_name, waybill, driver, vehicle, rate):
	trip = frappe.get_doc({
		"doctype": "Freight Trip", "company": company,
		"trip_date": today(), "route": route_name,
		"prime_mover": vehicle, "driver": driver,
		"waybill": waybill, "agreed_rate": rate,
	})
	trip.insert(ignore_permissions=True)
	trip.submit()
	return trip.name


def _create_expenses(company, trip_name):
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
	events = [
		("Booked", "Dar es Salaam", None),
		("Departed Origin", "Morogoro", None),
		("In Transit", "Dodoma", None),
	]
	for status, location, hub in events:
		try:
			trk = frappe.get_doc({
				"doctype": "Shipment Tracking", "company": company,
				"freight_trip": trip_name, "timestamp": now(),
				"status": status, "location": location,
				"is_customer_visible": 1,
			})
			trk.insert(ignore_permissions=True)
			trk.submit()
		except Exception:
			frappe.db.rollback()
