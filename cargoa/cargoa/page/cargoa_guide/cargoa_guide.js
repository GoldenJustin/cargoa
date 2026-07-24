frappe.pages["cargoa-guide"].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({parent:wrapper, title:__("Cargoa Test Guide"), single_column:true});
    $(wrapper).find(".layout-main-section").html(`
    <div style="padding:24px;max-width:920px;margin:0 auto;">
        <div style="background:linear-gradient(135deg,#1a73e8,#4285f4);color:#fff;padding:28px;border-radius:12px;margin-bottom:24px;">
            <h1 style="margin:0 0 6px;font-size:26px;">🚚 Cargoa Test Guide</h1>
            <p style="margin:0;opacity:.9;font-size:15px;">Logistics Operations Engine</p>
        </div>
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:20px;margin-bottom:20px;">
            <h3 style="margin:0 0 8px;color:#15803d;">⚡ Load Demo Data</h3>
            <p style="margin:0 0 8px;">In bench console:</p>
            <pre style="background:#1a1a2e;color:#4ade80;padding:14px;border-radius:6px;font-size:13px;margin:0;">from cargoa.cargoa.demo import create_demo_data
create_demo_data()</pre>
        </div>
        <h2 style="margin:24px 0 12px;font-size:20px;">📋 Full Flow</h2>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#1a73e8;">1. Master Data</b><br><span style="color:#555;">Create Freight Routes (with fuel benchmarks), Drivers, Vehicles. Check Cargoa Settings.</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#1a73e8;">2. Delivery Order</b><br><span style="color:#555;">Customer request. Estimated cost auto-calculs from Tariff.</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#1a73e8;">3. Waybill</b><br><span style="color:#555;">Record cargo, weight, loading/offloading points.</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#1a73e8;">4. Freight Trip (HUB)</b><br><span style="color:#555;">Link route+vehicle+driver+waybill. Set rate. Revenue auto-calculates.</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#e67e22;">5. Trip Expenses</b><br><span style="color:#555;">Each cost auto-creates a Journal Entry. P&L updates live.</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#9b59b6;">6. Shipment Tracking</b><br><span style="color:#555;">Log checkpoints. Trip status auto-updates.</span>
        </div>
        <div style="background:#fff;border:2px solid #27ae60;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#27ae60;">7. Submit Trip → Auto-Accounting ✨</b><br>
            <span style="color:#555;">Creates Sales Invoice + Purchase Invoice (hired truck) + Payment Entry (hired driver).</span>
        </div>
        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
            <b style="color:#1a73e8;">8. Reports</b><br><span style="color:#555;">Trip Profitability, Fleet Utilization, Driver Performance, Revenue Analysis, Fuel Analysis, Vehicle Cost.</span>
        </div>
    </div>`);
};
