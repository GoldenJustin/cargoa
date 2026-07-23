# -*- coding: utf-8 -*-
"""
Hooks for Cargoa — Logistics Operations Engine.
"""

app_name = "cargoa"
app_title = "Cargoa"
app_publisher = "Cargoa"
app_description = "Logistics Operations Engine — Fleet, Freight, Tracking, Billing & Reporting"
app_icon = "octicon octicon-package"
app_color = "#1a73e8"
app_email = "support@cargoa.app"
app_license = "MIT"

before_install = "cargoa.cargoa.setup.before_install"
after_install = "cargoa.cargoa.setup.after_install"

doc_events = {
	"*": {
		"on_cancel": ["cargoa.cargoa.api.on_voucher_cancel"],
	},
}

# Scheduled tasks (auto-billing, etc.)
scheduler_events = {
	"daily": [
		"cargoa.cargoa.tasks.daily_maintenance",
	],
}
