# -*- coding: utf-8 -*-
"""
Installation / setup routines for the Logistics Management app.

These run when you do ``bench --site <site> install-app logistics_management``.

Order of operations handled here (robust regardless of framework sync order):

1. ``before_install``  -> create the two Logistics roles.
2. ``after_install``   -> grant permissions, add the accounting link fields
   on the standard ERPNext accounting doctypes, create the default
   "Logistics Settings" record and a couple of sample service Items.
"""
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

LOGISTICS_DOCTYPES = [
	"Freight Route",
	"Driver",
	"Transport Vehicle",
	"Logistics Settings",
	"Waybill",
	"Trip Expense",
	"Freight Trip",
	"Trip Settlement",
]


# ------------------------------------------------------------------
# Hooks
# ------------------------------------------------------------------
def before_install():
	ensure_roles()


def after_install():
	ensure_roles()
	add_logistics_permissions()
	create_custom_accounting_fields()
	create_default_settings()
	create_sample_items()
	frappe.db.commit()
	frappe.msgprint(_("Logistics Management app has been installed successfully."))


# ------------------------------------------------------------------
# Roles
# ------------------------------------------------------------------
def ensure_roles():
	"""Create Logistics Manager & Logistics User roles if missing."""
	for role_name, defaults in (
		("Logistics Manager", {"desk_access": 1, "search_bar": 1}),
		("Logistics User", {"desk_access": 1, "search_bar": 1}),
	):
		if not frappe.db.exists("Role", role_name):
			doc = frappe.get_doc(
				{"doctype": "Role", "role_name": role_name, **defaults}
			)
			doc.insert(ignore_permissions=True)


# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
FULL_PTYPES = ["read", "write", "create", "delete", "submit", "cancel",
			   "amend", "print", "email", "report", "import", "export", "share"]
USER_PTYPES = ["read", "write", "create", "submit", "cancel",
			   "print", "email", "report", "share"]


def add_logistics_permissions():
	"""Grant the Logistics roles access to the doctypes of this app."""
	try:
		for dt in LOGISTICS_DOCTYPES:
			if not frappe.db.exists("DocType", dt):
				continue
			# Logistics Manager = full control
			_grant(dt, "Logistics Manager", FULL_PTYPES)
			# Logistics User = day-to-day operations, no delete / amend
			user_ptypes = ["read", "report", "email", "print", "share"] if dt == "Logistics Settings" else USER_PTYPES
			_grant(dt, "Logistics User", user_ptypes)
	except Exception as e:  # nosec - never break the install for permissions
		frappe.log_error(title="Logistics: permission setup", message=e)


def _grant(doctype, role, ptypes):
	try:
		frappe.permissions.add_permission(doctype, role, 0)
		for ptype in ptypes:
			frappe.permissions.update_permission_property(doctype, role, 0, ptype, 1)
	except Exception as e:  # nosec
		frappe.log_error(title=f"Logistics: grant {role} on {doctype}", message=e)


# ------------------------------------------------------------------
# Accounting link fields on standard doctypes
# ------------------------------------------------------------------
def create_custom_accounting_fields():
	"""
	Add a 'Freight Trip' link on the standard accounting doctypes so every
	Invoice / Entry / Payment can be traced back to the journey that created it.
	"""
	try:
		create_custom_fields(
			{
				"Sales Invoice": [
					dict(fieldname="freight_trip", label="Freight Trip",
						 fieldtype="Link", options="Freight Trip",
						 insert_after="customer", allow_on_submit=1,
						 description="The journey that generated this revenue."),
				],
				"Purchase Invoice": [
					dict(fieldname="freight_trip", label="Freight Trip",
						 fieldtype="Link", options="Freight Trip",
						 insert_after="supplier", allow_on_submit=1,
						 description="The journey this cost belongs to (e.g. hired truck)."),
				],
				"Journal Entry": [
					dict(fieldname="freight_trip", label="Freight Trip",
						 fieldtype="Link", options="Freight Trip",
						 insert_after="user_remark", allow_on_submit=1,
						 description="The journey this entry belongs to."),
				],
				"Payment Entry": [
					dict(fieldname="freight_trip", label="Freight Trip",
						 fieldtype="Link", options="Freight Trip",
						 insert_after="party", allow_on_submit=1,
						 description="The journey this payment belongs to."),
				],
			}
		)
	except Exception as e:  # nosec
		frappe.log_error(title="Logistics: custom fields", message=e)


# ------------------------------------------------------------------
# Default settings + sample items
# ------------------------------------------------------------------
def create_default_settings():
	"""Create the single 'Logistics Settings' record and seed sensible defaults."""
	try:
		if not frappe.db.exists("Logistics Settings", "Logistics Settings"):
			settings = frappe.new_doc("Logistics Settings")
			settings.insert(ignore_permissions=True)
		else:
			settings = frappe.get_doc("Logistics Settings")

		company = (
			frappe.db.get_single_value("Global Defaults", "default_company")
			if not settings.company
			else settings.company
		)
		if company:
			settings.company = company
			company_doc = frappe.get_cached_doc("Company", company)
			settings.default_cost_center = settings.default_cost_center or company_doc.cost_center
			settings.default_payable_account = (
				settings.default_payable_account or company_doc.default_payable_account
			)
			settings.default_bank_account = (
				settings.default_bank_account or getattr(company_doc, "default_bank_account", None)
			)
			settings.default_cash_account = (
				settings.default_cash_account or getattr(company_doc, "default_cash_account", None)
			)
			settings.freight_income_account = (
				settings.freight_income_account or getattr(company_doc, "default_income_account", None)
			)
			# default expense account used for any category not individually mapped
			default_exp = getattr(company_doc, "default_expense_account", None)
			for f in ("truck_hire_account", "fuel_account", "allowance_account",
					  "fines_tolls_account", "repairs_account",
					  "offloading_loading_account", "other_expense_account"):
				if not settings.get(f):
					settings.set(f, default_exp)
			settings.save(ignore_permissions=True)
	except Exception as e:  # nosec
		frappe.log_error(title="Logistics: default settings", message=e)


def create_sample_items():
	"""Create two service items used to bill freight and to pay hired trucks."""
	settings = frappe.get_doc("Logistics Settings")
	items = [
		("Freight Charges", "Transportation / freight service charged to the customer."),
		("Truck Hire", "Hire of a third-party (hired) prime mover / truck for a trip."),
	]
	for code, desc in items:
		try:
			if not frappe.db.exists("Item", code):
				frappe.get_doc(
					{
						"doctype": "Item",
						"item_code": code,
						"item_name": code,
						"item_group": "Services",
						"stock_uom": "Nos",
						"is_stock_item": 0,
						"description": desc,
					}
				).insert(ignore_permissions=True)
		except Exception as e:  # nosec
			frappe.log_error(title=f"Logistics: sample item {code}", message=e)

	try:
		settings.freight_income_item = settings.freight_income_item or "Freight Charges"
		settings.truck_hire_item = settings.truck_hire_item or "Truck Hire"
		settings.save(ignore_permissions=True)
	except Exception as e:  # nosec
		frappe.log_error(title="Logistics: link sample items", message=e)
