# -*- coding: utf-8 -*-
"""
Logistics Settings - the single configuration record that maps every
logistics concept to the Chart of Accounts.

This is the bridge between the operational side (trips, expenses, allowances)
and the accounting side (Invoices, Journal Entries, Payments). All the
money-flow automation reads from here.
"""
import frappe
from frappe import _
from frappe.model.document import Document


class LogisticsSettings(Document):
	def validate(self):
		account_fields = [
			"freight_income_account", "truck_hire_account", "fuel_account",
			"allowance_account", "fines_tolls_account", "repairs_account",
			"offloading_loading_account", "other_expense_account",
			"default_payable_account", "default_bank_account", "default_cash_account",
		]
		if self.company:
			for f in account_fields:
				account = self.get(f)
				if account:
					acc_company = frappe.db.get_value("Account", account, "company")
					if acc_company and acc_company != self.company:
						frappe.throw(
							_("Account {0} does not belong to company {1}.").format(account, self.company)
						)
