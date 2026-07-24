frappe.pages["cargoa-guide"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Cargoa — Test Guide & Demo"),
		single_column: true,
	});

	$(wrapper).find(".layout-main-section").html(`
	<div style="padding: 24px; max-width: 920px; margin: 0 auto;">

		<div style="background: linear-gradient(135deg, #1a73e8, #4285f4); color: #fff; padding: 28px; border-radius: 12px; margin-bottom: 24px;">
			<h1 style="margin:0 0 6px; font-size: 26px;">🚚 Cargoa Test Guide</h1>
			<p style="margin:0; opacity:.9; font-size:15px;">Logistics Operations Engine — Fleet, Freight, Tracking, Billing & Reporting</p>
		</div>

		<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
			<h3 style="margin:0 0 8px; color:#15803d;">⚡ Quick Demo — Load Sample Data</h3>
			<p style="margin:0 0 10px; color:#333;">Run in <code style="background:#1a1a2e; color:#4ade80; padding:2px 8px; border-radius:4px;">bench --site YOURSITE console</code>:</p>
			<pre style="background:#1a1a2e; color:#a5b1c2; padding:14px; border-radius:6px; overflow-x:auto; font-size:13px; margin:0;">from cargoa.cargoa.demo import create_demo_data
create_demo_data()</pre>
			<p style="margin:8px 0 0; color:#555; font-size:13px;">Creates 2 routes, 3 drivers, 3 vehicles, 2 customers, 2 waybills, 2 trips, 5 expenses, tracking events.</p>
		</div>

		<h2 style="color:#333; margin: 28px 0 14px; font-size:20px;">📋 Step-by-Step Full Flow</h2>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#1a73e8;">Step 1 — Set Up Master Data</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				<b>Freight Routes</b> → create a route (e.g. Dar → Mwanza, 1180km, 320L fuel benchmark).<br>
				<b>Drivers</b> (Own Employee or Hired Contractor), <b>Transport Vehicles</b> (Owned or Hired).<br>
				<b>Cargoa Settings</b> → verify accounts auto-filled from your company.
			</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#1a73e8;">Step 2 — Create a Delivery Order</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				<b>Delivery Order → Add</b>. Pick customer, cargo, weight, origin/destination.<br>
				The <b>estimated cost auto-calculates</b> from your Tariff. Submit → status becomes Confirmed.
			</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#1a73e8;">Step 3 — Create a Waybill</h3>
			<p style="margin:4px 0 0; color:#555;">Record what's being carried: customer, cargo, weight, loading/offloading points. Submit.</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#1a73e8;">Step 4 — Create a Freight Trip (THE HUB)</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				Link route + vehicle + driver + waybill. Set Agreed Rate.<br>
				<b>Revenue auto-calculates</b> = Weight × Rate. Save (don't submit yet).
			</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#e67e22;">Step 5 — Log Trip Expenses</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				Create one per cost: Fuel (enter liters!), Allowance, Fine, Toll, Repair.<br>
				Each Company-paid expense <b>auto-creates a Journal Entry</b>. The trip P&L updates live.
			</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#9b59b6;">Step 6 — Track the Shipment</h3>
			<p style="margin:4px 0 0; color:#555;">Log checkpoints: Picked Up → In Transit → At Hub → Delivered. Trip status auto-updates.</p>
		</div>

		<div style="background:#fff; border:2px solid #27ae60; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#27ae60;">Step 7 — Submit the Trip → Auto-Accounting ✨</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				Review live P&L, then <b>Submit</b>. Cargoa automatically creates:<br>
				• <b>Sales Invoice</b> to the customer (revenue)<br>
				• <b>Purchase Invoice</b> to truck owner (if hired)<br>
				• <b>Payment Entry</b> to pay hired driver<br>
				All linked to the trip, all posting to the GL.
			</p>
		</div>

		<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px; color:#1a73e8;">Step 8 — Reconcile & Report</h3>
			<p style="margin:4px 0 0; color:#555; line-height:1.7;">
				<b>Trip Settlement</b> → enter cash received/paid → full money-flow chain.<br>
				<b>Reports:</b> Trip Profitability, Fleet Utilization, Driver Performance, Revenue Analysis, Fuel Analysis, Vehicle Cost.
			</p>
		</div>

		<div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:16px 20px; margin-top:20px;">
			<h3 style="margin:0 0 8px; color:#92400e;">💡 Key Things to Verify</h3>
			<ul style="margin:0; padding-left:20px; color:#555; line-height:2;">
				<li>Fuel Variance shows red if actual &gt; benchmark → <b>theft detection</b></li>
				<li>Negative-margin trips warn in red</li>
				<li>Hired trucks get a Purchase Invoice on trip submit</li>
				<li>Dashboard shows 6 KPI cards + 4 charts that update with data</li>
				<li>All 6 reports work with date/route/customer filters</li>
			</ul>
		</div>

		<p style="text-align:center; margin-top:28px; color:#999; font-size:13px;">Cargoa v2.0 — Logistics Operations Engine</p>
	</div>
	`);
};
