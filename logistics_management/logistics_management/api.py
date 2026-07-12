# -*- coding: utf-8 -*-
"""
Whitelisted server methods for the Logistics app.

These power the buttons on the Freight Trip form and implement the
"money flow" chain:

    REVENUE (money IN)  : Freight Trip -> Sales Invoice -> Payment Entry (receipt)
    HIRED TRUCK         : Freight Trip -> Purchase Invoice -> Payment Entry (payment)
    EXPENSES            : Trip Expense -> Journal Entry (auto)
    HIRED DRIVER PAY    : Freight Trip -> Payment Entry (payment to driver's supplier)
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def get_settings():
	return frappe.get_doc("Logistics Settings")


def _trip_company_cost_center(trip_doc):
	settings = get_settings()
	company = trip_doc.company or settings.company
	cost_center = trip_doc.cost_center or settings.default_cost_center
	return settings, company, cost_center


# ------------------------------------------------------------------
# REVENUE: Freight Trip -> Sales Invoice
# ------------------------------------------------------------------
@frappe.whitelist()
def create_sales_invoice(trip):
	trip_doc = frappe.get_doc("Freight Trip", trip)
	if trip_doc.sales_invoice:
		frappe.throw(_("Sales Invoice already created: {0}").format(trip_doc.sales_invoice))
	if not trip_doc.customer:
		frappe.throw(_("Please set a Customer on the Freight Trip before billing."))
	if flt(trip_doc.total_revenue) <= 0:
		frappe.throw(_("Total Revenue must be greater than 0 before creating a Sales Invoice."))

	settings, company, cost_center = _trip_company_cost_center(trip_doc)

	si = frappe.new_doc("Sales Invoice")
	si.customer = trip_doc.customer
	si.company = company
	si.posting_date = nowdate()
	si.cost_center = cost_center
	si.set("freight_trip", trip)  # custom field
	si.due_date = nowdate()
	si.append(
		"items",
		{
			"item_code": settings.freight_income_item or "Freight Charges",
			"qty": 1,
			"rate": flt(trip_doc.total_revenue),
			"income_account": settings.freight_income_account,
			"cost_center": cost_center,
			"description": _("Freight for trip {0} ({1})").format(trip, trip_doc.route or ""),
		},
	)
	si.set_missing_values()
	try:
		si.run_method("calculate_taxes_and_totals")
	except Exception:
		pass
	si.insert(ignore_permissions=True)
	frappe.db.set_value("Freight Trip", trip, "sales_invoice", si.name)
	frappe.msgprint(_("Draft Sales Invoice {0} created.").format(si.name))
	return si.name


# ------------------------------------------------------------------
# HIRED TRUCK: Freight Trip -> Purchase Invoice (to truck owner)
# ------------------------------------------------------------------
@frappe.whitelist()
def create_truck_hire_invoice(trip):
	trip_doc = frappe.get_doc("Freight Trip", trip)
	if trip_doc.purchase_invoice:
		frappe.throw(_("Truck Hire Purchase Invoice already created: {0}").format(trip_doc.purchase_invoice))

	vehicle = frappe.get_doc("Transport Vehicle", trip_doc.prime_mover) if trip_doc.prime_mover else None
	if not vehicle or vehicle.ownership_type != "Hired" or not vehicle.linked_supplier:
		frappe.throw(_("The selected Prime Mover is not a hired truck, or has no owner (Supplier) linked."))
	if flt(trip_doc.truck_hire_rate) <= 0:
		frappe.throw(_("Please set the Truck Hire Rate on the Freight Trip first."))

	settings, company, cost_center = _trip_company_cost_center(trip_doc)

	pi = frappe.new_doc("Purchase Invoice")
	pi.supplier = vehicle.linked_supplier
	pi.company = company
	pi.posting_date = nowdate()
	pi.cost_center = cost_center
	pi.set("freight_trip", trip)  # custom field
	pi.append(
		"items",
		{
			"item_code": settings.truck_hire_item or "Truck Hire",
			"qty": 1,
			"rate": flt(trip_doc.truck_hire_rate),
			"expense_account": settings.truck_hire_account,
			"cost_center": cost_center,
			"description": _("Hire of truck {0} for trip {1}").format(trip_doc.prime_mover, trip),
		},
	)
	pi.set_missing_values()
	pi.insert(ignore_permissions=True)
	frappe.db.set_value("Freight Trip", trip, "purchase_invoice", pi.name)
	frappe.msgprint(_("Draft Purchase Invoice {0} created for truck owner {1}.").format(pi.name, vehicle.linked_supplier))
	return pi.name


# ------------------------------------------------------------------
# HIRED DRIVER PAYMENT: Freight Trip -> Payment Entry (pay driver)
# ------------------------------------------------------------------
@frappe.whitelist()
def pay_driver(trip):
	trip_doc = frappe.get_doc("Freight Trip", trip)
	driver = frappe.get_doc("Driver", trip_doc.driver) if trip_doc.driver else None
	if not driver or driver.driver_type != "Hired Contractor" or not driver.linked_supplier:
		frappe.throw(_("The driver is not a hired contractor or has no Supplier linked."))
	if flt(trip_doc.total_allowances) <= 0:
		frappe.throw(_("There are no driver allowances to pay on this trip."))

	settings, company, cost_center = _trip_company_cost_center(trip_doc)
	paid_from = settings.default_bank_account or settings.default_cash_account
	if not paid_from:
		frappe.throw(_("Set a default Bank / Cash account in Logistics Settings."))

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Pay"
	pe.party_type = "Supplier"
	pe.party = driver.linked_supplier
	pe.company = company
	pe.posting_date = nowdate()
	pe.paid_from = paid_from
	pe.paid_amount = flt(trip_doc.total_allowances)
	pe.received_amount = flt(trip_doc.total_allowances)
	pe.cost_center = cost_center
	pe.set("freight_trip", trip)  # custom field
	pe.remark = _("Driver allowance for trip {0}").format(trip)
	pe.setup_party_account_field()
	pe.set_missing_values()
	pe.insert(ignore_permissions=True)
	frappe.db.set_value("Freight Trip", trip, "driver_payment", pe.name)
	frappe.msgprint(_("Draft Payment Entry {0} created to pay driver {1}.").format(pe.name, driver.driver_name))
	return pe.name


# ------------------------------------------------------------------
# Receive customer payment: Freight Trip -> Payment Entry (receipt)
# Convenience wrapper around standard ERPNext, but pre-linked to the trip.
# ------------------------------------------------------------------
@frappe.whitelist()
def receive_customer_payment(trip, amount=None):
	trip_doc = frappe.get_doc("Freight Trip", trip)
	if not trip_doc.customer:
		frappe.throw(_("No customer on this trip."))
	if not trip_doc.sales_invoice:
		frappe.throw(_("Create the Sales Invoice first."))

	settings, company, cost_center = _trip_company_cost_center(trip_doc)
	received_to = settings.default_bank_account or settings.default_cash_account
	if not received_to:
		frappe.throw(_("Set a default Bank account in Logistics Settings."))

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = trip_doc.customer
	pe.company = company
	pe.posting_date = nowdate()
	pe.paid_to = received_to
	pe.paid_amount = flt(amount) if amount else flt(trip_doc.total_revenue)
	pe.received_amount = pe.paid_amount
	pe.cost_center = cost_center
	pe.set("freight_trip", trip)
	pe.setup_party_account_field()
	pe.set_paid_amount()
	pe.set_missing_values()
	# link it against the sales invoice
	pe.append(
		"references",
		{
			"reference_doctype": "Sales Invoice",
			"reference_name": trip_doc.sales_invoice,
			"total_amount": flt(trip_doc.total_revenue),
			"allocated_amount": pe.paid_amount,
		},
	)
	pe.insert(ignore_permissions=True)
	frappe.msgprint(_("Draft Payment Entry {0} created.").format(pe.name))
	return pe.name


# ------------------------------------------------------------------
# Hook: keep trip figures fresh when a linked accounting doc is cancelled
# ------------------------------------------------------------------
def recalc_trip_from_voucher(doc, method=None):
	trip = doc.get("freight_trip")
	if trip:
		# import lazily to avoid circular import
		from logistics_management.logistics_management.doctype.freight_trip.freight_trip import update_trip_costs

		update_trip_costs(trip)
