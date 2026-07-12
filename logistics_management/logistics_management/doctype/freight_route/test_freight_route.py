# -*- coding: utf-8 -*-
"""
Sample unit test for Freight Route. Run with:

    bench --site <site> run-tests --doctype "Freight Route"

These tests are executed inside the bench/python environment, which is why
they import frappe directly.
"""
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from logistics_management.logistics_management.doctype.freight_route.freight_route import FreightRoute


class TestFreightRoute(FrappeTestCase):
	def test_create_route(self):
		route = frappe.get_doc(
			{
				"doctype": "Freight Route",
				"route_name": "_Test Route Dar - Mwanza",
				"origin": "Dar es Salaam",
				"destination": "Mwanza",
				"total_distance_km": 1180,
				"trip_type": "One-Way",
				"standard_fuel_allocation": 320,
				"standard_driver_allowance": 150000,
			}
		)
		route.insert()
		self.assertEqual(route.origin, "Dar es Salaam")
		self.assertTrue(flt(route.standard_fuel_allocation) > 0)
		route.delete()

	def test_same_origin_destination_rejected(self):
		route = frappe.get_doc(
			{
				"doctype": "Freight Route",
				"route_name": "_Test Bad Route",
				"origin": "Dodoma",
				"destination": "Dodoma",
				"total_distance_km": 10,
			}
		)
		self.assertRaises(frappe.ValidationError, route.insert)
