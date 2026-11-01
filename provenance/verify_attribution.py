#!/usr/bin/env python3
"""RAFAELIA fork attribution evidence gate (stdlib-only, no rights adjudication).

Checks listed file blobs and prevents platform/upstream/local evidence conflation.
An exact Git blob is evidence of bytes, NOT of legal authorship or CI execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ORIGINS = {
    "INHERITED_CANDIDATE", "BUNDLED_THIRD_PARTY_CANDIDATE",
    "MIXED_UNRESOLVED", "LOCAL_ADDED_CANDIDATE",
    "LOCAL_REUSE_OF_LOCAL_CANDIDATE",
}
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_EXTERNAL = {
    "PLATFORM_PROVIDER", "THIRD_PARTY_ACTION_DEPENDENCY", "UPSTREAM_PROJECT",
}


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def check(snapshot, root):
    errors = []
    if snapshot.get("schema") != "rafaelia.actions.attribution-snapshot/v2":
        errors.append("unsupported schema")
    if snapshot.get("repository") != "rafaelmeloreisnovo/actions":
        errors.append("repository identity mismatch")
    if snapshot.get("upstream_repository") != "gradle/actions":
        errors.append("upstream authority mismatch")
    if snapshot.get("github_actions_platform") != "GITHUB_HOSTED_EXTERNAL_SERVICE_NOT_REPO_CODE":
        errors.append("GitHub Actions platform conflated with repository source")
    for field in ("whole_repository_original_authorship_claim", "exclusive_rights_proven",
                  "release_allowed", "ci_pass_at_observed_head"):
        if snapshot.get(field) is not False:
            errors.append(field + " must be explicitly false")
    if snapshot.get("ci_evidence_state") != "NO_WORKFLOW_RUN_RETURNED_FOR_OBSERVED_HEAD_OR_PR22_HEAD_AT_AUDIT":
        errors.append("CI evidence must not be upgraded without separate provider receipt")
    if not SHA1.fullmatch(str(snapshot.get("observed_source_commit", ""))):
        errors.append("invalid observed source commit")
    ext = snapshot.get("external_authorities")
    if not isinstance(ext, list) or {item.get("role") for item in ext if isinstance(item, dict)} != ALLOWED_EXTERNAL:
        errors.append("platform/vendor/upstream attribution boundaries missing")
    records = snapshot.get("files")
    if not isinstance(records, list) or not records:
        return errors + ["missing file census"]
    seen = {}
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append("record %d is not an object" % i)
            continue
        path = rec.get("path")
        if not isinstance(path, str) or not path or "\\" in path or path.startswith("/") or any(
            p in ("", ".", "..") for p in path.split("/")
        ):
            errors.append("unsafe path at record %d" % i)
            continue
        if path in seen:
            errors.append("duplicate path " + path)
            continue
        seen[path] = rec
        blob = rec.get("blob")
        if not isinstance(blob, str) or not SHA1.fullmatch(blob):
            errors.append("invalid blob for " + path)
        if rec.get("origin") not in ORIGINS:
            errors.append("unapproved origin for " + path)
        if not isinstance(rec.get("provenance"), str) or len(rec["provenance"]) < 15:
            errors.append("missing provenance note for " + path)
        if not isinstance(rec.get("rights"), str) or len(rec["rights"]) < 10:
            errors.append("missing rights state for " + path)
        file_path = root / path
        if file_path.is_symlink() or not file_path.is_file():
            errors.append("missing or linked file " + path)
            continue
        if git_blob_sha1(file_path.read_bytes()) != blob:
            errors.append("file blob drift " + path)
        other = rec.get("same_blob_as")
        if rec.get("origin") == "LOCAL_REUSE_OF_LOCAL_CANDIDATE" and not other:
            errors.append("local reuse lacks ancestry " + path)
        if other and rec.get("origin") != "LOCAL_REUSE_OF_LOCAL_CANDIDATE":
            errors.append("reuse classification mismatch " + path)
    for path, rec in seen.items():
        other = rec.get("same_blob_as")
        if other and (other not in seen or seen[other].get("blob") != rec.get("blob") or other == path):
            errors.append("same-blob provenance invalid " + path)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("attribution_snapshot.v2.json"))
    opts = parser.parse_args(argv)
    try:
        data = json.loads(opts.manifest.read_text(encoding="utf-8"))
        problems = check(data, opts.root.resolve())
    except (OSError, ValueError, TypeError) as exc:
        print("ATTRIBUTION_BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    for problem in problems:
        print("ATTRIBUTION_BLOCKED: " + problem, file=sys.stderr)
    if problems:
        return 1
    print("ATTRIBUTION_SNAPSHOT_PASS: scoped blobs validated; legal rights, platform CI and physical runs NOT proved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
