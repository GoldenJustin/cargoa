// Module path: cargoa.cargoa.api
var API = "cargoa.cargoa.api.";
frappe.ui.form.on("Freight Trip", {
    setup: function(frm) {
        frm.set_query("prime_mover", function(){ return {filters:{is_active:1}}; });
        frm.set_query("trailer", function(){ return {filters:{is_active:1,vehicle_type:"Trailer"}}; });
        frm.set_query("driver", function(){ return {filters:{is_active:1}}; });
    },
    refresh: function(frm) {
        if (frm.doc.__islocal || frm.doc.docstatus!==1) return;
        if (!frm.doc.sales_invoice && frm.doc.customer && flt(frm.doc.total_revenue)>0)
            frm.add_custom_button(__("Sales Invoice"), function(){ _c(frm,API+"create_sales_invoice","Sales Invoice"); }, __("Create"));
        if (frm.doc.vehicle_ownership_type==="Hired" && !frm.doc.purchase_invoice && flt(frm.doc.truck_hire_rate)>0)
            frm.add_custom_button(__("Truck Hire"), function(){ _c(frm,API+"create_truck_hire_invoice","Purchase Invoice"); }, __("Create"));
        if (frm.doc.driver_type==="Hired Contractor" && !frm.doc.driver_payment && flt(frm.doc.total_allowances)>0)
            frm.add_custom_button(__("Pay Driver"), function(){ _c(frm,API+"pay_driver","Payment Entry"); }, __("Create"));
    },
});
function _c(frm,m,dt){ frappe.call({method:m,args:{trip:frm.doc.name},freeze:true,callback:function(r){ if(r.message){frm.refresh();frappe.set_route("Form",dt,r.message);} }}); }
