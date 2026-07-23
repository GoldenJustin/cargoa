# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

CATEGORY_ACCOUNT_FIELD = {
	"Fuel": "fuel_account", "Driver Allowance (Posho)": "allowance_account",
	"Weighbridge Fine": "fines_tolls_account", "Toll Gate": "fines_tolls_account",
	"En-route Repair": "repairs_account", "Offloading Fee": "offloading_loading_account",
	"Loading Fee": "offloading_loading_account", "Truck Hire": "truck_hire_account",
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
			try:
				from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
				update_trip_costs(self.freight_trip)
			except Exception:
				pass
		if self.paid_by == "Company":
			self.make_journal_entry()

	def on_cancel(self):
		if self.freight_trip:
			try:
				from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
				update_trip_costs(self.freight_trip)
			except Exception:
				pass
		self.cancel_journal_entry()

	def make_journal_entry(self):
		settings = frappe.get_doc("Cargoa Settings")
		company = self.company or settings.company
		if not company:
			company = frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			return
		c = frappe.get_cached_doc("Company", company)
		cost_center = (frappe.db.get_value("Freight Trip", self.freight_trip, "cost_center")
			or settings.default_cost_center or getattr(c, "cost_center", None))
		field = CATEGORY_ACCOUNT_FIELD.get(self.expense_category, "other_expense_account")
		debit_account = settings.get(field) or getattr(c, "default_expense_account", None)
		if self.supplier:
			credit_account = settings.default_payable_account or getattr(c, "default_payable_account", None)
		else:
			credit_account = (settings.default_bank_account or settings.default_cash_account
				or getattr(c, "default_bank_account", None) or getattr(c, "default_cash_account", None))
		if not debit_account or not credit_account:
			frappe.msgprint(_("Accounts not configured. Run seed_settings() or set Cargoa Settings."), indicator="orange")
			return
		try:
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Journal Entry"
			je.posting_date = self.expense_date
			je.company = company
			je.user_remark = "{0} | {1} | Trip {2}".format(self.expense_category, self.name, self.freight_trip)
			je.set("freight_trip", self.freight_trip)
			je.append("accounts", {"account": debit_account, "debit_in_account_currency": flt(self.amount), "cost_center": cost_center})
			credit_row = {"account": credit_account, "credit_in_account_currency": flt(self.amount), "cost_center": cost_center}
			if self.supplier:
				credit_row["party_type"] = "Supplier"
				credit_row["party"] = self.supplier
			je.append("accounts", credit_row)
			je.insert(ignore_permissions=True)
			if settings.get("auto_submit_accounting") and je.docstatus == 0:
				je.submit()
			self.db_set("journal_entry", je.name)
		except Exception as e:
			frappe.msgprint(_("Could not create Journal Entry: {0}").format(str(e)), indicator="red")

	def cancel_journal_entry(self):
		if self.journal_entry and frappe.db.exists("Journal Entry", self.journal_entry):
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:
					je.cancel()
				elif je.docstatus == 0:
					je.delete()
			except Exception:
				pass
