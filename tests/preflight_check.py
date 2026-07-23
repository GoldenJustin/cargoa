#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRE-FLIGHT CHECK for Cargoa. Run BEFORE pushing:
    python3 tests/preflight_check.py
"""
import ast, json, os, sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []

def ok(msg): print("  [OK]   " + msg)
def err(msg): errors.append(msg); print("  [FAIL] " + msg)

def main():
	print("=" * 60)
	print("  CARGOA — PRE-FLIGHT CHECK")
	print("=" * 60)

	# 1. Scaffold
	print("\n=== 1. Scaffold ===")
	for f in ["setup.py", "cargoa/__init__.py", "cargoa/hooks.py", "cargoa/modules.txt",
		"cargoa/cargoa/__init__.py", "cargoa/cargoa/setup.py", "cargoa/cargoa/api.py"]:
		if os.path.exists(os.path.join(APP_DIR, f)): ok(f)
		else: err("MISSING: " + f)

	# 2. No circular imports
	print("\n=== 2. __init__.py check ===")
	for root, dirs, files in os.walk(APP_DIR):
		dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
		for fn in files:
			if fn == "__init__.py":
				path = os.path.join(root, fn)
				src = open(path).read()
				if "from . import __version__" in src:
					err("CIRCULAR IMPORT in " + os.path.relpath(path, APP_DIR))
				else: ok(os.path.relpath(path, APP_DIR))

	# 3. Python syntax
	print("\n=== 3. Python syntax ===")
	count = 0
	for root, dirs, files in os.walk(APP_DIR):
		dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
		for fn in files:
			if fn.endswith(".py"):
				path = os.path.join(root, fn); count += 1
				try: ast.parse(open(path).read())
				except SyntaxError as e: err("Syntax error in " + os.path.relpath(path, APP_DIR) + ": " + str(e))
	ok(str(count) + " Python files parsed")

	# 4. JSON
	print("\n=== 4. JSON validity ===")
	count = 0
	for root, dirs, files in os.walk(APP_DIR):
		dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
		for fn in files:
			if fn.endswith(".json"):
				path = os.path.join(root, fn); count += 1
				try: json.load(open(path))
				except Exception as e: err("Bad JSON in " + os.path.relpath(path, APP_DIR) + ": " + str(e))
	ok(str(count) + " JSON files valid")

	# 5. Doctype crash checks
	print("\n=== 5. Doctype checks ===")
	dt_dir = os.path.join(APP_DIR, "cargoa", "cargoa", "doctype")
	for name in sorted(os.listdir(dt_dir)):
		jp = os.path.join(dt_dir, name, name + ".json")
		if not os.path.exists(jp): continue
		d = json.load(open(jp))
		if d.get("issingle"):
			if "engine" in d: err(name + ": Single has 'engine' (CRASH)")
			elif "autoname" in d: err(name + ": Single has 'autoname' (CRASH)")
			else: ok(name + ": Single clean")
		elif d.get("module") != "Cargoa":
			err(name + ": wrong module '" + str(d.get("module")) + "'")
		elif d.get("links") and any(l.get("link_doctype") in ("Sales Invoice","Purchase Invoice","Journal Entry","Payment Entry") for l in d["links"]):
			err(name + ": cross-doctype links (CRASH)")
		else: ok(name + ": clean")

	print("\n" + "=" * 60)
	if errors:
		print("  RESULT: " + str(len(errors)) + " ERROR(S) — FIX BEFORE PUSHING")
		for e in errors: print("    - " + e)
		sys.exit(1)
	else:
		print("  RESULT: ALL CHECKS PASSED — SAFE TO PUSH")
		sys.exit(0)

if __name__ == "__main__":
	main()
