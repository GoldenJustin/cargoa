cargoa.cargoa.page.cargoa_guide.cargoa_guide.render = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Cargoa — Test Guide & Demo",
		single_column: true,
	});

	$(wrapper).find(".layout-main-section").html(`
	<div style="padding: 24px; max-width: 900px; margin: 0 auto;">

		<div style="background: linear-gradient(135deg, #1a73e8, #4285f4); color: #fff; padding: 28px; border-radius: 12px; margin-bottom: 24px;">
			<h1 style="margin:0 0 6px; font-size: 28px;">🚚 Cargoa Test Guide</h1>
			<p style="margin:0; opacity:.85;">Full logistics operations engine — test the complete flow step by step.</p>
		</div>

		<div style="background: #fff; border: 1px solid #e8e8e8; border-radius: 8px; padding: 20px; margin-bottom: 16px; border-left: 4px solid #27ae60;">
			<h3 style="margin:0 0 8px; color:#27ae60;">⚡ Quick Start — Load Demo Data</h3>
			<p style="margin:0 0 10px; color:#555;">Run this in <code>bench --site YOURSITE console</code> to create sample routes, drivers, vehicles, customers, waybills, trips, expenses & tracking:</p>
			<pre style="background:#1a1a2e; color:#a5b1c2; padding:14px; border-radius:6px; overflow-x:auto; font-size:13px;">from cargoa.cargoa.demo import create_demo_data
create_demo_data()</pre>
		</div>

		<h2 style="color:#333; margin: 28px 0 14px;">📋 Step-by-Step Flow</h2>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#3498db; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">1</span> Set Up Master Data</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				Go to <b>Cargoa → Freight Routes</b> → create a route (e.g. Dar es Salaam → Mwanza, 1180 km, 320L fuel benchmark).<br>
				Then <b>Drivers</b> (Own Employee or Hired Contractor), <b>Transport Vehicles</b> (Owned or Hired), and <b>Cargoa Settings</b> (check accounts auto-filled).
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#3498db; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">2</span> Create a Delivery Order</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Delivery Order → Add</b>. Pick customer, cargo, weight, origin/destination. The <b>estimated cost auto-calculates</b> from your Tariff. Submit → status becomes Confirmed.
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#3498db; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">3</span> Create a Waybill</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Waybill → Add</b>. Record what's being carried: customer, cargo description, weight, loading/offloading points. Submit.
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#3498db; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">4</span> Create a Freight Trip (THE HUB)</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Freight Trip → Add</b>. Link the route, vehicle, driver, and waybill. Set the Agreed Rate. <b>Revenue auto-calculates</b> = Weight × Rate. Save (don't submit yet).
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#e67e22; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">5</span> Log Trip Expenses</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Trip Expense → Add</b>. Create one per cost: Fuel (enter liters!), Driver Allowance, Weighbridge Fine, Toll, Repair. Each <b>Company-paid expense auto-creates a Journal Entry</b>. Submit each → the trip's P&L updates live.
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#9b59b6; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">6</span> Track the Shipment</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Shipment Tracking → Add</b>. Log each checkpoint: Picked Up → In Transit → At Hub → Delivered. The trip status auto-updates.
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px; border-left:4px solid #27ae60;">
			<h3 style="margin:0 0 6px;"><span style="background:#27ae60; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">7</span> Submit the Trip → Auto-Accounting</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				Review the live P&L on the Freight Trip, then <b>Submit</b>. Cargoa automatically creates:<br>
				• <b>Sales Invoice</b> (to the customer for total revenue)<br>
				• <b>Purchase Invoice</b> (to the truck owner, if hired)<br>
				• <b>Payment Entry</b> (to pay a hired driver)<br>
				All linked to the trip, all posting to the General Ledger.
			</p>
		</div>

		<div class="step" style="background:#fff; border:1px solid #e8e8e8; border-radius:8px; padding:16px 20px; margin-bottom:10px;">
			<h3 style="margin:0 0 6px;"><span style="background:#3498db; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px;">8</span> Reconcile & Report</h3>
			<p style="margin:4px 0; color:#555; line-height:1.7;">
				<b>Cargoa → Trip Settlement</b> → enter cash received/paid → see the full money-flow chain.<br>
				<b>Reports:</b> Trip Profitability, Fleet Utilization, Driver Performance, Revenue Analysis, Fuel Analysis, Vehicle Cost Report.
			</p>
		</div>

		<div style="background:#fff3cd; border:1px solid #ffeaa7; border-radius:8px; padding:16px 20px; margin-top:20px;">
			<h3 style="margin:0 0 8px; color:#856404;">💡 Key Things to Verify</h3>
			<ul style="margin:0; padding-left:20px; color:#555; line-height:2;">
				<li>Fuel Variance (L) shows red if actual &gt; benchmark → <b>theft detection</b></li>
				<li>Negative margin trips warn in red at save time</li>
				<li>Hired trucks get a Purchase Invoice automatically on trip submit</li>
				<li>Each Trip Expense creates a Journal Entry (check the Accounting section)</li>
				<li>The dashboard shows 6 KPI cards + 4 charts that update as you add data</li>
				<li>All 6 reports work with date/route/customer filters</li>
			</ul>
		</div>

		<p style="text-align:center; margin-top:28px; color:#999; font-size:13px;">Cargoa v2.0 — Logistics Operations Engine</p>
	</div>
	`);
};
