#!/usr/bin/env python3
"""HOST-ONLY path, Git blob identity and graph validation; no provider authority."""
import hashlib
import json
from pathlib import Path
import re
import sys

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def main():
    module = Path(__file__).resolve().parents[1]
    root = module.parents[1]
    data = json.loads((module / "navigation.v1.json").read_text(encoding="utf-8"))
    nodes = data["source_nodes"]
    known = {x["id"] for x in nodes}
    if len(known) != len(nodes):
        raise ValueError("duplicate node")
    if data["claims"]["merge_authorized"] or data["claims"]["claim_allowed"] or data["claims"]["remote_ci_pass"]:
        raise ValueError("invalid promotion claim")
    for n in nodes:
        file = (root / n["path"]).resolve()
        if root not in file.parents or not file.is_file():
            raise ValueError("missing/out-of-scope: " + n["path"])
        claimed = n.get("git_blob_sha1")
        if claimed and (not re.fullmatch("[0-9a-f]{40}", claimed) or claimed != git_blob(file.read_bytes())):
            raise ValueError("blob mismatch: " + n["path"])
    for e in data["edges"]:
        if e["from"] not in known or e["to"] not in known:
            raise ValueError("dangling edge")
    for p in data["entrypoints"].values():
        if not (root / p).is_file():
            raise ValueError("missing entrypoint " + p)
    if len(data["demonstrations"]) != 4:
        raise ValueError("demo count invalid")
    print("NAVIGATION_PASS_SCOPED: %d nodes, %d edges, 4 scenarios; no merge rights" % (len(nodes), len(data["edges"])))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print("NAVIGATION_FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
