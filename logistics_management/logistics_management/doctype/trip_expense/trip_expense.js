// Trip Expense - client controller
// Convenience: when a Freight Trip is chosen, pull its company so the
// resulting Journal Entry is posted to the right books.
frappe.ui.form.on("Trip Expense", {
	freight_trip: function (frm) {
		if (frm.doc.freight_trip && !frm.doc.company) {
			frappe.db.get_value("Freight Trip", frm.doc.freight_trip, "company", function (r) {
				if (r && r.company) {
					frm.set_value("company", r.company);
				}
			});
		}
	},
});
