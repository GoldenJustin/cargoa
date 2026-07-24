#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast, json, os, sys
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
def ok(m): print("  [OK]  "+m)
def err(m): errors.append(m); print("  [FAIL] "+m)
def main():
    print("="*60+"\n  CARGOA v3 — PRE-FLIGHT\n"+"="*60)
    for root,dirs,files in os.walk(APP_DIR):
        dirs[:]=[d for d in dirs if d not in ("__pycache__",".git")]
        for fn in files:
            p=os.path.join(root,fn)
            if fn.endswith(".py"):
                try: ast.parse(open(p).read())
                except SyntaxError as e: err("PY: "+os.path.relpath(p,APP_DIR)+": "+str(e))
            elif fn.endswith(".json"):
                try: json.load(open(p))
                except Exception as e: err("JSON: "+os.path.relpath(p,APP_DIR)+": "+str(e))
    # doctype checks
    dtd=os.path.join(APP_DIR,"cargoa","cargoa","doctype")
    for name in sorted(os.listdir(dtd)):
        jp=os.path.join(dtd,name,name+".json")
        if not os.path.exists(jp): continue
        d=json.load(open(jp))
        if d.get("issingle"):
            if "engine" in d: err(name+": Single has engine")
            elif "autoname" in d: err(name+": Single has autoname")
        else:
            expected=d.get("name","").replace(" ","_").replace("-","_").lower()
            if expected!=name: err(f"{name}: name scrub mismatch '{expected}'")
            if d.get("module")!="Cargoa": err(name+": wrong module")
    # circular import check
    for root,dirs,files in os.walk(APP_DIR):
        dirs[:]=[d for d in dirs if d not in ("__pycache__",".git")]
        for fn in files:
            if fn=="__init__.py":
                s=open(os.path.join(root,fn)).read()
                if "from . import __version__" in s: err("CIRCULAR: "+fn)
    print("\n"+"="*60)
    if errors:
        print(f"  {len(errors)} ERROR(S) — FIX BEFORE PUSH")
        for e in errors: print("    - "+e)
        sys.exit(1)
    print("  ALL CHECKS PASSED — SAFE TO PUSH")
    sys.exit(0)
if __name__=="__main__": main()
