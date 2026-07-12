# -*- coding: utf-8 -*-
"""
Hooks for the Logistics Management app.
"""

app_name = "logistics_management"
app_title = "Logistics Management"
app_publisher = "Arena Logistics"
app_description = "Hub-and-Spoke Freight & Logistics Management for Frappe / ERPNext"
app_icon = "octicon octicon-package"
app_color = "#2980b9"
app_email = "support@example.com"
app_license = "MIT"

# ------------------------------------------------------------------
# Installation / Uninstallation
# ------------------------------------------------------------------
before_install = "logistics_management.logistics_management.setup.before_install"
after_install = "logistics_management.logistics_management.setup.after_install"

# ------------------------------------------------------------------
# DocType events
# Keep accounting figures in sync with the Freight Trip (the Hub).
# Most logic lives inside the controllers, but we expose a couple of
# hooks here so cancellations from the accounting side also refresh the trip.
# ------------------------------------------------------------------
doc_events = {
	"on_cancel": {
		# When an invoice/entry linked to a trip is cancelled, recalc the trip.
		"Sales Invoice": "logistics_management.logistics_management.api.recalc_trip_from_voucher",
		"Purchase Invoice": "logistics_management.logistics_management.api.recalc_trip_from_voucher",
		"Journal Entry": "logistics_management.logistics_management.api.recalc_trip_from_voucher",
	},
}

# Auto-created roles are handled in before_install / after_install.
# (See logistics_management/logistics_management/setup.py)

# ------------------------------------------------------------------
# Period accounting defaults are stored in the "Logistics Settings" doctype.
# ------------------------------------------------------------------
