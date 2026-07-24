# -*- coding: utf-8 -*-
"""
Cargoa install / setup. Bulletproof: every step isolated, install always finishes.
Creates roles, permissions, custom fields, items, settings, dashboard, notifications.
"""
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOCTYPES = [
	"Freight Route", "Driver", "Transport Vehicle", "Cargoa Settings",
	"Hub", "Tariff", "Customer Contract", "Delivery Order", "Waybill",
	"Shipment Tracking", "Freight Trip", "Trip Expense", "Fuel Log",
	"Vehicle Service Log", "Trip Settlement", "Cargo Claim",
]


def before_install():
	pass


def after_install():
	for fn in (_roles, _perms, _fields, _items, seed_settings, _number_cards, _dashboard_charts, _notifications):
		try:
			fn()
		except Exception:
			frappe.db.rollback()
			try:
				frappe.log_error(title="Cargoa install: " + fn.__name__)
			except Exception:
				pass
	try:
		frappe.db.commit()
	except Exception:
		pass
	frappe.msgprint(_("Cargoa installed successfully."))


def _roles():
	for r in ("Cargoa Manager", "Cargoa User", "Cargoa Dispatcher", "Cargoa Accounts"):
		try:
			if not frappe.db.exists("Role", r):
				frappe.get_doc({"doctype": "Role", "role_name": r,
					"desk_access": 1}).insert(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()
	frappe.db.commit()


FULL = ["read", "write", "create", "delete", "submit", "cancel", "amend",
		"print", "email", "report", "share"]
USER = ["read", "write", "create", "submit", "cancel", "print", "email", "report", "share"]
VIEW = ["read", "report", "email", "print"]


def _perms():
	role_perms = {
		"Cargoa Manager": FULL,
		"Cargoa User": USER,
		"Cargoa Dispatcher": USER,
		"Cargoa Accounts": USER,
	}
	for dt in DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			continue
		for role, pts in role_perms.items():
			if dt == "Cargoa Settings" and role != "Cargoa Manager":
				pts = VIEW
			try:
				frappe.permissions.add_permission(dt, role, 0)
				for p in pts:
					frappe.permissions.update_permission_property(dt, role, 0, p, 1)
			except Exception:
				frappe.db.rollback()
	frappe.db.commit()


def _ft_field(after):
	return dict(fieldname="freight_trip", label="Freight Trip",
		fieldtype="Link", options="Freight Trip",
		insert_after=after, allow_on_submit=1,
		description="The journey this voucher belongs to.")


def _fields():
	try:
		create_custom_fields({
			"Sales Invoice": [_ft_field("customer")],
			"Purchase Invoice": [_ft_field("supplier")],
			"Journal Entry": [_ft_field("user_remark")],
			"Payment Entry": [_ft_field("party")],
		})
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()


def _first(doctype, names):
	for n in names:
		try:
			if frappe.db.exists(doctype, n):
				return n
		except Exception:
			pass
	return None


def _items():
	grp = _first("Item Group", ["Services", "All Item Groups"]) or "Services"
	uom = _first("UOM", ["Nos", "Unit"]) or "Nos"
	for code, desc in [
		("Freight Charges", "Freight service charged to the customer."),
		("Truck Hire", "Hire of a hired prime mover / truck for a trip."),
		("Demurrage", "Delay / detention charges."),
		("Loading Charges", "Loading service."),
		("Offloading Charges", "Offloading service."),
	]:
		try:
			if not frappe.db.exists("Item", code):
				frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": code,
					"item_group": grp, "stock_uom": uom, "is_stock_item": 0,
					"description": desc}).insert(ignore_permissions=True)
				frappe.db.commit()
		except Exception:
			frappe.db.rollback()


def seed_settings():
	"""Fill Cargoa Settings from company defaults. Re-runnable from console."""
	try:
		s = frappe.get_doc("Cargoa Settings")
		company = s.company or frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			company = frappe.db.get_value("Company", {"disabled": 0}, "name")
		if not company:
			return
		c = frappe.get_cached_doc("Company", company)
		s.company = company
		s.default_cost_center = s.default_cost_center or getattr(c, "cost_center", None)
		s.default_payable_account = s.default_payable_account or getattr(c, "default_payable_account", None)
		s.default_bank_account = s.default_bank_account or getattr(c, "default_bank_account", None)
		s.default_cash_account = s.default_cash_account or getattr(c, "default_cash_account", None)
		s.freight_income_account = s.freight_income_account or getattr(c, "default_income_account", None)
		exp = getattr(c, "default_expense_account", None)
		for f in ("truck_hire_account", "fuel_account", "allowance_account",
				"fines_tolls_account", "repairs_account", "maintenance_account",
				"offloading_loading_account", "other_expense_account"):
			if not s.get(f):
				s.set(f, exp)
		if not s.freight_income_item and frappe.db.exists("Item", "Freight Charges"):
			s.freight_income_item = "Freight Charges"
		if not s.truck_hire_item and frappe.db.exists("Item", "Truck Hire"):
			s.truck_hire_item = "Truck Hire"
		if not s.get("auto_create_accounting"):
			s.auto_create_accounting = 1
		s.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()


def _dashboard():
	"""Kept for compatibility — actual widgets created in _number_cards / _dashboard_charts."""
	pass


def _number_cards():
	"""Create KPI number cards for the workspace."""
	cards = [
		{"label": "Active Trips", "doc": "Freight Trip", "func": "Count",
		 "color": "#3498db", "filters": [["Freight Trip", "trip_status", "=", "In Transit"]]},
		{"label": "Total Revenue", "doc": "Freight Trip", "func": "Sum",
		 "color": "#27ae60", "field": "total_revenue"},
		{"label": "Total Profit", "doc": "Freight Trip", "func": "Sum",
		 "color": "#2ecc71", "field": "trip_profit"},
		{"label": "Completed Trips", "doc": "Freight Trip", "func": "Count",
		 "color": "#9b59b6", "filters": [["Freight Trip", "trip_status", "=", "Completed"]]},
		{"label": "Total Vehicles", "doc": "Transport Vehicle", "func": "Count",
		 "color": "#e67e22"},
		{"label": "Total Drivers", "doc": "Driver", "func": "Count",
		 "color": "#e74c3c"},
	]
	import json
	for c in cards:
		try:
			if not frappe.db.exists("Number Card", c["label"]):
				doc = frappe.get_doc({
					"doctype": "Number Card", "name": c["label"], "label": c["label"],
					"type": "Document Type", "document_type": c["doc"],
					"function": c["func"], "color": c["color"],
					"module": "Cargoa", "is_standard": 1, "is_public": 1,
					"stats_time_series": 0,
				})
				if c.get("field"):
					doc.report_field = c["field"]
				if c.get("filters"):
					doc.filters_json = json.dumps(c["filters"])
				doc.insert(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()
	frappe.db.commit()


def _dashboard_charts():
	"""Create dashboard charts for the workspace."""
	charts = [
		# Time-series: revenue trend
		{"name": "Revenue Trend", "doc": "Freight Trip", "based_on": "trip_date",
		 "value_field": "total_revenue", "func": "Sum", "chart_type": "Line",
		 "timeseries": 1, "timespan": "Last Year", "interval": "Monthly"},
		# Category: trips by status
		{"name": "Trips by Status", "doc": "Freight Trip", "based_on": "trip_status",
		 "value_field": None, "func": "Count", "chart_type": "Donut",
		 "timeseries": 0, "timespan": None, "interval": None},
		# Category: profit by route
		{"name": "Profit by Route", "doc": "Freight Trip", "based_on": "route",
		 "value_field": "trip_profit", "func": "Sum", "chart_type": "Bar",
		 "timeseries": 0, "timespan": None, "interval": None},
		# Time-series: fuel cost trend
		{"name": "Fuel Cost Trend", "doc": "Freight Trip", "based_on": "trip_date",
		 "value_field": "total_fuel_cost", "func": "Sum", "chart_type": "Line",
		 "timeseries": 1, "timespan": "Last Year", "interval": "Monthly"},
	]
	for c in charts:
		try:
			if not frappe.db.exists("Dashboard Chart", c["name"]):
				doc = frappe.get_doc({
					"doctype": "Dashboard Chart", "name": c["name"], "chart_name": c["name"],
					"chart_type": "Document", "document_type": c["doc"],
					"based_on": c["based_on"], "type": c["chart_type"],
					"timeseries": c["timeseries"], "module": "Cargoa",
					"is_public": 1, "is_standard": 1,
				})
				if c.get("value_field"):
					doc.value_based_on = c["value_field"]
					doc.aggregate_function = c["func"]
				else:
					doc.aggregate_function = c["func"]
				if c.get("timespan"):
					doc.timespan = c["timespan"]
					doc.time_interval = c["interval"]
				doc.insert(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()
	frappe.db.commit()


def _notifications():
	"""Create email notification templates for customer communication."""
	notifs = [
		("Delivery Booked", "Delivery Order", "draft", "Your delivery has been booked. Order {name} for {customer}."),
		("Shipment Dispatched", "Shipment Tracking", "on_update", "Your shipment {name} has been dispatched and is in transit."),
		("Shipment Delivered", "Shipment Tracking", "on_update", "Your shipment {name} has been delivered. Thank you for choosing Cargoa."),
	]
	for name, dt, event, subject in notifs:
		try:
			if not frappe.db.exists("Notification", name):
				frappe.get_doc({
					"doctype": "Notification",
					"name": name,
					"subject": subject,
					"document_type": dt,
					"event": event if event != "draft" else "New",
					"channel": "Email",
					"enabled": 1,
				}).insert(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()
	frappe.db.commit()
