# -*- coding: utf-8 -*-
"""
Trip Expense - logs every shilling spent while the truck is on the road.

On submit it:
  1. Refreshes the rolled-up cost & profit figures on the linked Freight Trip.
  2. (If the Company paid) posts a Journal Entry to the books, debiting the
     expense head for the category and crediting the payable (if a supplier is
     owed) or the bank/cash account. The Journal Entry is linked back to the trip.

On cancel the figures are refreshed and the Journal Entry is reversed.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

# Maps an Expense Category to the Logistics Settings field that holds its account.
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
		if self.expense_category == "Fuel" and not flt(self.quantity):
			frappe.msgprint(
				_("Tip: enter the Quantity in Liters so the trip can detect excess fuel consumption."),
				indicator="orange",
			)

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
	def get_expense_account(self, settings):
		field = CATEGORY_ACCOUNT_FIELD.get(self.expense_category, "other_expense_account")
		return settings.get(field)

	def make_journal_entry(self):
		settings = frappe.get_doc("Logistics Settings")
		company = self.company or settings.company
		if not company:
			frappe.msgprint(_("No company set. Skipping Journal Entry."), indicator="orange")
			return

		cost_center = (
			frappe.db.get_value("Freight Trip", self.freight_trip, "cost_center")
			or settings.default_cost_center
		)
		debit_account = self.get_expense_account(settings)

		if self.supplier:
			credit_account = settings.default_payable_account or frappe.db.get_value(
				"Company", company, "default_payable_account"
			)
		else:
			credit_account = settings.default_bank_account or settings.default_cash_account

		if not debit_account or not credit_account:
			frappe.msgprint(
				_(
					"Expense or credit account not configured in Logistics Settings. "
					"Journal Entry was not created for this expense."
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

		je.append(
			"accounts",
			{
				"account": debit_account,
				"debit_in_account_currency": flt(self.amount),
				"cost_center": cost_center,
			},
		)

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
