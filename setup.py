# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = [
		line.strip()
		for line in f.read().split("\n")
		if line.strip() and not line.startswith("#")
	]

setup(
	name="logistics_management",
	version="1.0.0",
	description="Hub-and-Spoke Freight & Logistics Management for Frappe / ERPNext",
	author="Arena Logistics",
	author_email="support@example.com",
	url="https://example.com/logistics_management",
	license="MIT",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
