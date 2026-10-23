#!/usr/bin/env python3
"""Fail-closed static validation; deliberately not an execution or promotion gate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "composition" / "next_steps.v1.json"
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_STATES = {"NEXT", "BLOCKED", "DEFERRED"}


def validate(data, root=ROOT):
    errors = []
    if data.get("schema") != "rafaelia.actions.composition/v1":
        errors.append("schema mismatch")
    if data.get("repository") != "rafaelmeloreisnovo/actions":
        errors.append("repository mismatch")
    if data.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    if data.get("scope") != "NAVIGATION_AND_STATIC_GATE_ONLY":
        errors.append("static validation must not claim runtime proof")
    for literal in ("SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM",
                    "TOKEN_VAZIO != 0", "IMPLEMENTED_UNTESTED != PASS",
                    "CI_PASS != PHYSICAL_PASS"):
        if literal not in data.get("principles", []):
            errors.append("missing principle: " + literal)
    lanes = data.get("lanes", [])
    lane_ids = [x.get("id") for x in lanes]
    if not lane_ids or len(set(lane_ids)) != len(lane_ids):
        errors.append("missing or duplicate lane id")
    for lane in lanes:
        if not lane.get("proof_scope"):
            errors.append("lane missing proof scope")
        if not str(lane.get("current_evidence", "")).startswith("TOKEN_VAZIO_"):
            errors.append("lane cannot assert evidence from static contract")
        paths = list(lane.get("source_paths", []))
        if lane.get("workflow"):
            paths.append(lane["workflow"])
        if not paths:
            errors.append("lane missing routes")
        for relative in paths:
            p = Path(relative)
            if p.is_absolute() or ".." in p.parts or not (root / p).is_file():
                errors.append("missing or unsafe source path: " + str(relative))
    steps = data.get("steps", [])
    ids = [s.get("id") for s in steps]
    if not ids or len(set(ids)) != len(ids):
        errors.append("missing or duplicate step id")
    graph = {}
    for step in steps:
        sid = step.get("id")
        if step.get("priority") not in VALID_PRIORITIES:
            errors.append("invalid priority for " + str(sid))
        if step.get("state") not in VALID_STATES:
            errors.append("state is not fail-closed for " + str(sid))
        if step.get("lane") not in lane_ids:
            errors.append("undefined lane for " + str(sid))
        if step.get("claim_allowed", False) is not False:
            errors.append("illegal promotion for " + str(sid))
        for k in ("action", "acceptance", "evidence_rule", "rollback"):
            if not step.get(k):
                errors.append("missing " + k + " for " + str(sid))
        if not str(step.get("gap", "")).startswith("TOKEN_VAZIO_"):
            errors.append("untyped unresolved gap for " + str(sid))
        deps = step.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append("dependencies must be a list for " + str(sid))
            deps = []
        graph[sid] = deps
    state = {}
    def visit(n):
        if state.get(n) == 1:
            errors.append("dependency cycle: " + str(n))
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for dep in graph.get(n, []):
            if dep not in graph:
                errors.append("undefined dependency: " + str(dep))
            else:
                visit(dep)
        state[n] = 2
    for sid in graph:
        visit(sid)
    return errors


if __name__ == "__main__":
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    failures = validate(data)
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        raise SystemExit(1)
    print("PASS: composition static contract (NOT runtime/release evidence)")
