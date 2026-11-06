#!/usr/bin/env python3
"""Conservative selected-file license router. No copyright/legal clearance claims."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "rafaelia.actions.license-scopes/v1"
UPSTREAM = "gradle/actions"
REPO = "rafaelmeloreisnovo/actions"
SHA = re.compile(r"^[0-9a-f]{40}$")
CATEGORIES = {"INHERITED", "BUNDLED", "MIXED", "LOCAL_CANDIDATE", "LOCAL_REUSE_HOLD", "META_ONLY"}
REQUIRED = {
    "LICENSE": ("INHERITED", "LICENSE"),
    "action.yml": ("INHERITED", "LICENSE"),
    "setup-gradle/": ("INHERITED", "LICENSE"),
    "dist/": ("BUNDLED", "LICENSES/MIXED_AND_BUNDLED_HOLD.md"),
    ".github/": ("MIXED", "LICENSES/MIXED_AND_BUNDLED_HOLD.md"),
    "freestanding/kernel4/": ("LOCAL_CANDIDATE", "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md"),
    "freestanding/entry_l0/": ("LOCAL_CANDIDATE", "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md"),
    "freestanding/provenance_core/": ("LOCAL_CANDIDATE", "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md"),
    "android/atlas_wizard/native/atlas.c": ("LOCAL_REUSE_HOLD", "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md"),
}
ZERO_GRANT_FIELDS = ("legal_clearance_verified", "exclusive_authorship_proven",
                     "physical_arm_execution_proven", "actions_service_freestanding",
                     "whole_repo_authorial", "new_license_grant_issued", "release_allowed", "claim_allowed")


def safe_path(path):
    return (isinstance(path, str) and bool(path) and not path.startswith("/")
            and "\\" not in path and all(piece not in ("", ".", "..") for piece in path.rstrip("/").split("/"))
            and "**" not in path and "*" not in path and "?" not in path
            and (path.rstrip("/") != ""))


def real_regular(root, path):
    if not safe_path(path):
        return None
    parent = root
    for component in path.rstrip("/").split("/"):
        parent = parent / component
        if parent.is_symlink():
            return None
    if not parent.is_file():
        return None
    return parent


def blob_id(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def resolve(path, records):
    matching = [r for r in records
                if path == r["path"] or (r["path"].endswith("/") and path.startswith(r["path"]))]
    if not matching:
        return None
    return max(matching, key=lambda r: len(r["path"]))


def check(data, root):
    errs = []
    if not isinstance(data, dict):
        return ["manifest not an object"]
    if data.get("schema") != SCHEMA or data.get("repository") != REPO or data.get("upstream") != UPSTREAM:
        errs.append("schema/repository/upstream identity mismatch")
    if not SHA.fullmatch(str(data.get("observed_main_sha", ""))):
        errs.append("invalid baseline commit")
    if data.get("scope") != "SELECTED_ROOTS_AND_EIGHT_EXACT_BLOB_FIXTURES_NOT_COMPLETE_CORPUS_CLEARANCE":
        errs.append("scope falsely expanded")
    if data.get("root_license") != "LICENSE" or data.get("upstream_notice_preserved") is not True:
        errs.append("inherited license notice lost")
    if data.get("protected_root_license_blob") != "b0c1c5227c57a4ffa546d29eece43e55e21db513":
        errs.append("root license identity changed")
    if data.get("authored_code_grant_state") != "TOKEN_VAZIO_UNSELECTED_HOLDER_REVIEW":
        errs.append("authorial license decision fabricated")
    for field in ZERO_GRANT_FIELDS:
        if data.get(field) is not False:
            errs.append(field + " must be false")
    records = data.get("paths")
    if not isinstance(records, list):
        return errs + ["missing path registry"]
    ids, roots = set(), set()
    verified_records = []
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            errs.append("non-object path record")
            continue
        path, kind, name, route = (rec.get("path"), rec.get("category"),
                                 rec.get("id"), rec.get("license_route"))
        if not safe_path(path) or not safe_path(route):
            errs.append("unsafe path/route at record %d" % i)
            continue
        if not isinstance(name, str) or not name or name in ids or path in roots:
            errs.append("duplicate/invalid scope identity " + str(path))
        ids.add(name)
        roots.add(path)
        if kind not in CATEGORIES:
            errs.append("unrecognized origin class for " + path)
        if not isinstance(rec.get("reason"), str) or len(rec["reason"]) < 15:
            errs.append("unexplained origin class for " + path)
        for field in ("license_grant_issued", "holder_verified", "claim_allowed"):
            if rec.get(field) is not False:
                errs.append("unauthorized promotion of " + field + " for " + path)
        expected_route = ("LICENSE" if kind == "INHERITED" else
                          "LICENSES/MIXED_AND_BUNDLED_HOLD.md" if kind in ("BUNDLED", "MIXED")
                          else "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md")
        if route != expected_route:
            errs.append("wrong license route for " + path)
        if path in REQUIRED and (kind, route) != REQUIRED[path]:
            errs.append("required origin/rights boundary changed for " + path)
        if real_regular(root, route) is None:
            errs.append("missing/unsafe license route " + str(route))
        verified_records.append(rec)
    for path in REQUIRED:
        if path not in roots:
            errs.append("required independent boundary absent " + path)
    for path in ("LICENSES/README.md", "LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md",
                 "LICENSES/MIXED_AND_BUNDLED_HOLD.md"):
        if real_regular(root, path) is None:
            errs.append("missing license gate document " + path)
    examples = data.get("examples")
    if not isinstance(examples, list) or len(examples) != 8:
        return errs + ["expected eight bounded blob fixtures"]
    by_path = {}
    for ex in examples:
        if not isinstance(ex, dict):
            errs.append("invalid blob fixture")
            continue
        path, blob, mid = ex.get("path"), ex.get("blob"), ex.get("module")
        if not safe_path(path) or path.endswith("/") or path in by_path:
            errs.append("unsafe or duplicate fixture path " + str(path))
            continue
        by_path[path] = ex
        if not SHA.fullmatch(str(blob)):
            errs.append("invalid Git blob " + path)
        rec = resolve(path, verified_records)
        if rec is None or rec["id"] != mid:
            errs.append("wrong file-origin partition " + path)
        file = real_regular(root, path)
        if file is None:
            errs.append("missing/linked fixture " + path)
        elif blob_id(file.read_bytes()) != blob:
            errs.append("byte drift " + path)
        same = ex.get("same_blob_as")
        if same and (same == path or not safe_path(same)):
            errs.append("invalid reuse target " + path)
    for path, ex in by_path.items():
        same = ex.get("same_blob_as")
        if same and (same not in by_path or
                     by_path[same].get("blob") != ex.get("blob")):
            errs.append("duplicate-source identity not preserved " + path)
    if {r["path"] for r in examples if isinstance(r, dict)} != {
        "LICENSE", "action.yml", "setup-gradle/action.yml",
        "freestanding/kernel4/kernel4.c", "freestanding/entry_l0/entry.c",
        "freestanding/provenance_core/rights_core.c",
        "freestanding/atlas_drive_l0/atlas.c", "android/atlas_wizard/native/atlas.c"}:
        errs.append("fixture allowlist mismatch")
    return errs


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("license_scopes.v1.json"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    opts = parser.parse_args(argv)
    try:
        errs = check(json.loads(opts.manifest.read_text(encoding="utf-8")), opts.root)
    except (OSError, ValueError, TypeError, KeyError) as error:
        errs = [str(error)]
    for e in errs:
        print("LICENSE_SCOPE_BLOCKED: " + e, file=sys.stderr)
    if errs:
        return 1
    print("LICENSE_SCOPE_PASS_SCOPED: origin and 8 blobs; rights NOT granted, release NOT approved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
