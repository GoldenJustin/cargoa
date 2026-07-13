# -*- coding: utf-8 -*-
"""Install / setup for Logistics Management. Every step is isolated so the
whole install always finishes. Logistics Settings is a SINGLE doctype."""
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOCTYPES = ["Freight Route", "Driver", "Transport Vehicle",
	"Waybill", "Trip Expense", "Freight Trip", "Trip Settlement"]


def before_install():
	pass


def after_install():
	for fn in (_roles, _perms, _fields, _items, seed_settings):
		try:
			fn()
		except Exception:
			frappe.db.rollback()
			try:
				frappe.log_error(title="Logistics install: " + fn.__name__)
			except Exception:
				pass
	frappe.db.commit()
	frappe.msgprint(_("Logistics Management installed successfully."))


def _roles():
	for r in ("Logistics Manager", "Logistics User"):
		if not frappe.db.exists("Role", r):
			frappe.get_doc({"doctype": "Role", "role_name": r, "desk_access": 1}).insert(ignore_permissions=True)
	frappe.db.commit()


FULL = ["read", "write", "create", "delete", "submit", "cancel", "amend", "print", "email", "report", "share"]
USER = ["read", "write", "create", "submit", "cancel", "print", "email", "report", "share"]


def _perms():
	for dt in DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			continue
		for role, pts in (("Logistics Manager", FULL), ("Logistics User", USER)):
			try:
				frappe.permissions.add_permission(dt, role, 0)
				for p in pts:
					frappe.permissions.update_permission_property(dt, role, 0, p, 1)
			except Exception:
				frappe.db.rollback()
	frappe.db.commit()


def _fields():
	def fld(after):
		return dict(fieldname="freight_trip", label="Freight Trip", fieldtype="Link",
			options="Freight Trip", insert_after=after, allow_on_submit=1)
	try:
		create_custom_fields({
			"Sales Invoice": [fld("customer")],
			"Purchase Invoice": [fld("supplier")],
			"Journal Entry": [fld("user_remark")],
			"Payment Entry": [fld("party")],
		})
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()


def _items():
	grp = next((x for x in ("Services", "All Item Groups") if frappe.db.exists("Item Group", x)), None) or frappe.db.get_value("Item Group", {}, "name") or "Services"
	uom = next((x for x in ("Nos", "Unit") if frappe.db.exists("UOM", x)), None) or "Nos"
	for code, desc in [("Freight Charges", "Freight service charged to the customer."), ("Truck Hire", "Hire of a hired prime mover / truck for a trip.")]:
		if not frappe.db.exists("Item", code):
			try:
				frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": code,
					"item_group": grp, "stock_uom": uom, "is_stock_item": 0, "description": desc}).insert(ignore_permissions=True)
				frappe.db.commit()
			except Exception:
				frappe.db.rollback()


def seed_settings():
	"""Fill Logistics Settings with company default accounts. Safe to re-run.
	Call from console if accounts are missing:
	    from logistics_management.logistics_management.setup import seed_settings
	    seed_settings()
	"""
	try:
		s = frappe.get_doc("Logistics Settings")

		# Resolve company
		company = s.company or frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			company = frappe.db.get_value("Company", {"disabled": 0}, "name")
		if not company:
			return  # nothing we can do

		c = frappe.get_cached_doc("Company", company)

		s.company = company
		s.default_cost_center = s.default_cost_center or c.cost_center or None
		s.default_payable_account = s.default_payable_account or getattr(c, "default_payable_account", None)
		s.default_bank_account = s.default_bank_account or getattr(c, "default_bank_account", None)
		s.default_cash_account = s.default_cash_account or getattr(c, "default_cash_account", None)
		s.freight_income_account = s.freight_income_account or getattr(c, "default_income_account", None)

		exp = getattr(c, "default_expense_account", None)
		for f in ("truck_hire_account", "fuel_account", "allowance_account",
				"fines_tolls_account", "repairs_account",
				"offloading_loading_account", "other_expense_account"):
			if not s.get(f):
				s.set(f, exp)

		# link service items
		if not s.freight_income_item and frappe.db.exists("Item", "Freight Charges"):
			s.freight_income_item = "Freight Charges"
		if not s.truck_hire_item and frappe.db.exists("Item", "Truck Hire"):
			s.truck_hire_item = "Truck Hire"

		# Enable auto-accounting by default
		if not s.get("auto_create_accounting"):
			s.auto_create_accounting = 1

		s.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
