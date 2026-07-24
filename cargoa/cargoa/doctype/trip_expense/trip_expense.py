# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
CAT_ACCT = {"Fuel":"fuel_account","Driver Allowance (Posho)":"allowance_account",
    "Weighbridge Fine":"fines_tolls_account","Toll Gate":"fines_tolls_account",
    "En-route Repair":"repairs_account","Offloading Fee":"offloading_loading_account",
    "Loading Fee":"offloading_loading_account","Truck Hire":"truck_hire_account","Other":"other_expense_account"}
class TripExpense(Document):
    def validate(self):
        if flt(self.amount)<=0: frappe.throw(_("Amount must be > 0."))
        if not self.expense_date: self.expense_date = nowdate()
    def on_submit(self):
        if self.freight_trip:
            try:
                from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
                update_trip_costs(self.freight_trip)
            except Exception: pass
        if self.paid_by=="Company": self.make_je()
    def on_cancel(self):
        if self.freight_trip:
            try:
                from cargoa.cargoa.doctype.freight_trip.freight_trip import update_trip_costs
                update_trip_costs(self.freight_trip)
            except Exception: pass
        self.cancel_je()
    def make_je(self):
        settings = frappe.get_doc("Cargoa Settings")
        company = self.company or settings.company
        if not company: company = frappe.db.get_single_value("Global Defaults","default_company")
        if not company: return
        c = frappe.get_cached_doc("Company", company)
        cc = frappe.db.get_value("Freight Trip", self.freight_trip, "cost_center") or settings.default_cost_center or getattr(c,"cost_center",None)
        field = CAT_ACCT.get(self.expense_category, "other_expense_account")
        debit = settings.get(field) or getattr(c,"default_expense_account",None)
        credit = (settings.default_payable_account or getattr(c,"default_payable_account",None)) if self.supplier else (settings.default_bank_account or settings.default_cash_account or getattr(c,"default_bank_account",None) or getattr(c,"default_cash_account",None))
        if not debit or not credit:
            frappe.msgprint(_("Accounts not configured. Run seed_settings()."), indicator="orange"); return
        try:
            je = frappe.new_doc("Journal Entry")
            je.voucher_type="Journal Entry"; je.posting_date=self.expense_date; je.company=company
            je.user_remark=f"{self.expense_category} | {self.name} | Trip {self.freight_trip}"
            je.set("freight_trip", self.freight_trip)
            je.append("accounts",{"account":debit,"debit_in_account_currency":flt(self.amount),"cost_center":cc})
            cr = {"account":credit,"credit_in_account_currency":flt(self.amount),"cost_center":cc}
            if self.supplier: cr["party_type"]="Supplier"; cr["party"]=self.supplier
            je.append("accounts", cr)
            je.insert(ignore_permissions=True)
            if settings.get("auto_submit_accounting") and je.docstatus==0: je.submit()
            self.db_set("journal_entry", je.name)
        except Exception as e: frappe.msgprint(_("JE error: {0}").format(str(e)), indicator="red")
    def cancel_je(self):
        if self.journal_entry and frappe.db.exists("Journal Entry", self.journal_entry):
            try:
                je = frappe.get_doc("Journal Entry", self.journal_entry)
                if je.docstatus==1: je.cancel()
                elif je.docstatus==0: je.delete()
            except Exception: pass
