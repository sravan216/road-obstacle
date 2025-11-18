#!/usr/bin/env python3
"""Top-level wrapper to run the nested project entrypoint.

This script switches the working directory into the nested project folder
and executes the existing `main.py` there. It makes it easier to run the
project from the repository root.
"""
import os
import sys
import runpy

ROOT = os.path.dirname(__file__)
NESTED_DIR = os.path.join(ROOT, 'road obstacle night')
NESTED_MAIN = os.path.join(NESTED_DIR, 'main.py')

if not os.path.exists(NESTED_MAIN):
    print(f"ERROR: nested main.py not found at: {NESTED_MAIN}")
    sys.exit(1)

# Change CWD so relative paths inside the nested main (config.yaml, model path)
# resolve as they did when running from the nested folder.
os.chdir(NESTED_DIR)

# Execute the nested main.py as __main__ so it behaves like a normal script.
runpy.run_path('main.py', run_name='__main__')
