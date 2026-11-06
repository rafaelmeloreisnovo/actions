#!/usr/bin/env python3
"""Fail-closed semantic validation of selected upstream contribution pointers."""
import json
from pathlib import Path
import sys

BASE = "c8a326d85724fce2ae59a38810306f4a058f26a4"
REPO = "rafaelmeloreisnovo/actions"
ALLOWED_STAGES = {"PATCH_DRAFT_UNTESTED", "BLOCKED_PRODUCER", "DESIGN_PENDING", "NEEDS_REPRO"}
EXPECTED = {549, 656, 316, 722, 813, 286, 1088}


def validate(doc):
    errors = []
    if doc.get("schema") != "rafaelia.upstream-contribution-roadmap/v1":
        errors.append("wrong schema")
    if doc.get("upstream") != "gradle/actions" or doc.get("fork") != REPO:
        errors.append("wrong authority")
    if doc.get("upstream_main_sha") != BASE:
        errors.append("unverified origin base")
    gate = doc.get("gate_policy", {})
    if not isinstance(gate, dict) or gate.get("provider_check_state") != "NONE_RETURNED_AS_OF_OBSERVATION":
        errors.append("provider test state cannot be silently promoted")
    for key in ("claim_allowed", "release_allowed", "allowed_merge_without_provider_pass"):
        if gate.get(key) is not False:
            errors.append("unverified promotion: " + key)
    if gate.get("upstream_submission_state") != "NOT_SUBMITTED":
        errors.append("unverified upstream submission")
    if gate.get("external_dco_attestation") != "TOKEN_VAZIO_NOT_ATTESTED":
        errors.append("unverified DCO attestation promoted")
    if gate.get("hard_deadline") is not None:
        errors.append("fabricated binding deadline")
    issues = doc.get("issues", [])
    if not isinstance(issues, list) or not issues:
        return errors + ["missing issue collection"]
    seen = set()
    patches = 0
    for issue in issues:
        if not isinstance(issue, dict):
            errors.append("non-object issue")
            continue
        identifier = issue.get("issue_id")
        if not isinstance(identifier, str) or not identifier.startswith("gradle/actions#"):
            errors.append("invalid issue id")
            continue
        try:
            number = int(identifier.rsplit("#", 1)[1])
        except ValueError:
            errors.append("bad issue number")
            continue
        if number in seen or issue.get("url") != f"https://github.com/gradle/actions/issues/{number}":
            errors.append("duplicate or incorrect issue locator")
        seen.add(number)
        if issue.get("stage") not in ALLOWED_STAGES:
            errors.append("unrecognized stage " + identifier)
        if issue.get("release_allowed") is not False or issue.get("claim_allowed") is not False:
            errors.append("unverified issue promotion " + identifier)
        if issue.get("hard_deadline") is not None:
            errors.append("fabricated external SLA " + identifier)
        cp = issue.get("checkpoint", {})
        if not isinstance(cp, dict) or cp.get("binding") is not False:
            errors.append("proposed checkpoint treated as binding " + identifier)
        if issue.get("patch_pr"):
            patches += 1
            if issue.get("stage") != "PATCH_DRAFT_UNTESTED":
                errors.append("patch test state promoted " + identifier)
            if issue.get("patch_base") != BASE or not issue.get("patch_pr", "").startswith(
                f"https://github.com/{REPO}/pull/"
            ):
                errors.append("wrong scoped patch base " + identifier)
            if not isinstance(issue.get("patch_head"), str) or len(issue["patch_head"]) != 40:
                errors.append("missing exact patch HEAD " + identifier)
        elif issue.get("patch_head") is not None:
            errors.append("patch HEAD without PR " + identifier)
    if seen != EXPECTED or patches != 2:
        errors.append("wrong bounded issue/patch census")
    edges = doc.get("typed_edges", [])
    if not isinstance(edges, list) or any(
        not isinstance(x, dict) or not all(x.get(k) for k in ("from", "type", "to"))
        for x in edges
    ):
        errors.append("invalid semantic edge")
    if not any(x.get("from") == "gradle/actions#316" and x.get("type") == "governed_by"
               and x.get("to") == "gradle/actions-caching" for x in edges if isinstance(x, dict)):
        errors.append("proprietary producer authority missing")
    if not any(x.get("from") == "gradle/actions#1088" and x.get("type") == "producer_unknown"
               and x.get("to") == "TOKEN_VAZIO" for x in edges if isinstance(x, dict)):
        errors.append("unknown producer fiction")
    return errors


def main():
    root = Path(__file__).resolve().parents[1]
    doc = json.loads((root / "provenance/upstream_issues_roadmap.v1.json").read_text())
    errors = validate(doc)
    for error in errors:
        print("UPSTREAM_ROUTE_BLOCKED: " + error, file=sys.stderr)
    if errors:
        return 1
    print("UPSTREAM_ROUTE_PASS_SCOPED: 7 issues / 2 draft patches; provider CI and licensing NOT_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
