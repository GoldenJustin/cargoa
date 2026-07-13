# -*- coding: utf-8 -*-
"""
Trip Expense - logs every shilling spent while the truck is on the road.

On submit it:
  1. Refreshes the rolled-up cost & profit figures on the linked Freight Trip.
  2. (If the Company paid) posts a Journal Entry to the books automatically.

Accounts are resolved from Logistics Settings first, falling back to the
Company's default accounts so the system works even before manual config.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

CATEGORY_ACCOUNT_FIELD = {
	"Fuel": "fuel_account",
	"Driver Allowance (Posho)": "allowance_account",
	"Weighbridge Fine": "fines_tolls_account",
	"Toll Gate": "fines_tolls_account",
	"En-route Repair": "repairs_account",
	"Offloading Fee": "offloading_loading_account",
	"Loading Fee": "offloading_loading_account",
	"Truck Hire": "truck_hire_account",
	"Other": "other_expense_account",
}


class TripExpense(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero."))
		if not self.expense_date:
			self.expense_date = nowdate()

	def on_submit(self):
		if self.freight_trip:
			from logistics_management.logistics_management.doctype.freight_trip.freight_trip import update_trip_costs
			update_trip_costs(self.freight_trip)

		if self.paid_by == "Company":
			self.make_journal_entry()

	def on_cancel(self):
		if self.freight_trip:
			from logistics_management.logistics_management.doctype.freight_trip.freight_trip import update_trip_costs
			update_trip_costs(self.freight_trip)
		self.cancel_journal_entry()

	# --------------------------------------------------------------
	# Accounting automation
	# --------------------------------------------------------------
	def _resolve_company(self, settings):
		company = self.company or settings.company
		if not company:
			company = frappe.db.get_single_value("Global Defaults", "default_company")
		return company

	def make_journal_entry(self):
		settings = frappe.get_doc("Logistics Settings")
		company = self._resolve_company(settings)
		if not company:
			frappe.msgprint(_("No company found. Skipping Journal Entry."), indicator="orange")
			return

		company_doc = frappe.get_cached_doc("Company", company)

		cost_center = (
			frappe.db.get_value("Freight Trip", self.freight_trip, "cost_center")
			or settings.default_cost_center
			or company_doc.cost_center
		)

		# --- Debit (expense) account: settings first, then company default ---
		field = CATEGORY_ACCOUNT_FIELD.get(self.expense_category, "other_expense_account")
		debit_account = settings.get(field) or getattr(company_doc, "default_expense_account", None)

		# --- Credit account: payable (if supplier) or bank/cash ---
		if self.supplier:
			credit_account = (
				settings.default_payable_account
				or getattr(company_doc, "default_payable_account", None)
			)
		else:
			credit_account = (
				settings.default_bank_account
				or settings.default_cash_account
				or getattr(company_doc, "default_bank_account", None)
				or getattr(company_doc, "default_cash_account", None)
			)

		if not debit_account or not credit_account:
			frappe.msgprint(
				_(
					"Accounts not fully configured. Open Logistics Settings and set the "
					"expense + bank/cash accounts, or run: "
					"bench --site YOURSITE console  >>>  "
					"from logistics_management.logistics_management.setup import seed_settings; seed_settings()"
				),
				indicator="orange",
			)
			return

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.expense_date
		je.company = company
		je.user_remark = "{0} | {1} | Trip {2}".format(
			self.expense_category, self.name, self.freight_trip
		)
		je.set("freight_trip", self.freight_trip)

		je.append("accounts", {
			"account": debit_account,
			"debit_in_account_currency": flt(self.amount),
			"cost_center": cost_center,
		})

		credit_row = {
			"account": credit_account,
			"credit_in_account_currency": flt(self.amount),
			"cost_center": cost_center,
		}
		if self.supplier:
			credit_row["party_type"] = "Supplier"
			credit_row["party"] = self.supplier
		je.append("accounts", credit_row)

		try:
			je.insert(ignore_permissions=True)
			if settings.auto_submit_accounting and je.docstatus == 0:
				je.submit()
			self.db_set("journal_entry", je.name)
		except Exception as e:
			frappe.msgprint(_("Could not create Journal Entry: {0}").format(str(e)), indicator="red")

	def cancel_journal_entry(self):
		if self.journal_entry and frappe.db.exists("Journal Entry", self.journal_entry):
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.cancel()
			elif je.docstatus == 0:
				je.delete()
