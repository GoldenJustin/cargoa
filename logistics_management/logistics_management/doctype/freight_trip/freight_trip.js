// Freight Trip - client controller
// Adds the buttons that create the accounting chain from the trip.
frappe.ui.form.on("Freight Trip", {
	setup: function (frm) {
		// Only show prime movers / trailers in the link dropdowns
		frm.set_query("prime_mover", function () {
			return {
				filters: { is_active: 1 },
			};
		});
		frm.set_query("trailer", function () {
			return {
				filters: { is_active: 1, vehicle_type: "Trailer" },
			};
		});
		frm.set_query("driver", function () {
			return {
				filters: { is_active: 1 },
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.__islocal) return;

		// --- Create the accounting chain (only when submitted) ---
		if (frm.doc.docstatus === 1) {
			// 1. Revenue -> Sales Invoice
			if (!frm.doc.sales_invoice && frm.doc.customer && flt(frm.doc.total_revenue) > 0) {
				frm.add_custom_button(
					__("Sales Invoice"),
					function () {
						create_and_open(frm, "logistics_management.api.create_sales_invoice", "Sales Invoice");
					},
					__("Create")
				);
			}

			// 2. Hired truck -> Purchase Invoice to owner
			if (
				frm.doc.vehicle_ownership_type === "Hired" &&
				!frm.doc.purchase_invoice &&
				flt(frm.doc.truck_hire_rate) > 0
			) {
				frm.add_custom_button(
					__("Truck Hire Invoice"),
					function () {
						create_and_open(frm, "logistics_management.api.create_truck_hire_invoice", "Purchase Invoice");
					},
					__("Create")
				);
			}

			// 3. Hired driver -> Payment Entry
			if (
				frm.doc.driver_type === "Hired Contractor" &&
				!frm.doc.driver_payment &&
				flt(frm.doc.total_allowances) > 0
			) {
				frm.add_custom_button(
					__("Pay Driver"),
					function () {
						create_and_open(frm, "logistics_management.api.pay_driver", "Payment Entry");
					},
					__("Create")
				);
			}
		}

		// Recalculate button (handy if data looks stale)
		frm.add_custom_button(__("Recalculate P&L"), function () {
			frappe.call({
				method: "frappe.client.save",
				args: { doc: frm.doc },
				callback: function () {
					frm.refresh();
				},
			});
		});
	},
});

function create_and_open(frm, method, open_doctype) {
	frappe.call({
		method: method,
		args: { trip: frm.doc.name },
		freeze: true,
		callback: function (r) {
			if (r.message) {
				frm.refresh();
				frappe.set_route("Form", open_doctype, r.message);
			}
		},
	});
}
