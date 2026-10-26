#!/usr/bin/env bash
# Source-bound, no network, no actions token. Invalid fixtures must fail.
set -euo pipefail
python3 -m unittest discover -s rafcode/evidence-receipt -p 'test_receipt.py' -q
python3 -m py_compile rafcode/evidence-receipt/issue_receipt.py
test -s "$RAF_FALSIFIER_ARTIFACT"
