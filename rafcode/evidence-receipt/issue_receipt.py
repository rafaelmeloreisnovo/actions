#!/usr/bin/env python3
"""First-party HOSTED CI receipt. Not an Android freestanding runtime component.

Executes one repository-owned shell falsifier with stripped credential environment.
Records exact Git HEAD, GitHub run metadata and bytes of a bounded artifact.
A successful output is PROVISIONAL until GitHub run and independent review pass.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SHA40 = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,79}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DIGITS = re.compile(r"^[1-9][0-9]{0,19}$")
MAX_ARTIFACT = 128 * 1024 * 1024
MAX_SCRIPT = 65536
SCHEMA = "rafaelia.rafcode.host-execution-receipt.v1"


class GateError(ValueError):
    pass


def _file_under(root: Path, raw: str, max_size: int) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 240 or raw.startswith("/"):
        raise GateError("UNSAFE_RELATIVE_PATH")
    pieces = raw.split("/")
    if any(part in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9._-]+", part)
           for part in pieces):
        raise GateError("UNSAFE_RELATIVE_PATH")
    target = root
    for part in pieces:
        target = target / part
        if target.is_symlink():
            raise GateError("SYMLINK_DENIED")
    if not target.is_file():
        raise GateError("REGULAR_FILE_REQUIRED")
    size = target.stat().st_size
    if size < 1 or size > max_size:
        raise GateError("FILE_SIZE_OUT_OF_BOUNDS")
    return target


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


def _git(root: Path, *args: str) -> str:
    command = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                             text=True, timeout=10, check=False)
    if command.returncode:
        raise GateError("GIT_COMMAND_FAILED")
    return command.stdout.strip()


def _append_file(raw: str, content: str) -> None:
    if raw:
        with Path(raw).open("a", encoding="utf-8") as out:
            out.write(content)


def issue_receipt(context: dict[str, str]) -> dict:
    required = ("GITHUB_WORKSPACE", "GITHUB_REPOSITORY", "GITHUB_RUN_ID",
                "GITHUB_RUN_ATTEMPT", "RAF_EXPECTED_SHA", "RAF_ARTIFACT_PATH",
                "RAF_FALSIFIER_SCRIPT", "RAF_FALSIFIER_ID")
    if any(not context.get(field) for field in required):
        raise GateError("CONTEXT_INCOMPLETE")
    expected = context["RAF_EXPECTED_SHA"]
    repo = context["GITHUB_REPOSITORY"]
    run_id, attempt = context["GITHUB_RUN_ID"], context["GITHUB_RUN_ATTEMPT"]
    fid = context["RAF_FALSIFIER_ID"]
    if (not SHA40.fullmatch(expected) or not REPO.fullmatch(repo)
            or not DIGITS.fullmatch(run_id) or not DIGITS.fullmatch(attempt)
            or not ID.fullmatch(fid)):
        raise GateError("CONTEXT_MALFORMED")
    workspace = Path(context["GITHUB_WORKSPACE"]).resolve(strict=True)
    if not (workspace / ".git").exists():
        raise GateError("MISSING_GIT_REPOSITORY")
    if _git(workspace, "rev-parse", "--verify", "HEAD") != expected:
        raise GateError("HEAD_DRIFT")
    if _git(workspace, "status", "--porcelain", "--untracked-files=no"):
        raise GateError("TRACKED_SOURCE_DIRTY")
    artifact = _file_under(workspace, context["RAF_ARTIFACT_PATH"], MAX_ARTIFACT)
    script = _file_under(workspace, context["RAF_FALSIFIER_SCRIPT"], MAX_SCRIPT)
    script_digest = _digest(script)
    # No secrets supplied by the runner survive in the child. A source-owned
    # script still must be reviewed; this is not an untrusted-code sandbox.
    allowed = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TZ", "CI")
    environment = {key: context[key] for key in allowed if context.get(key)}
    environment["RAF_FALSIFIER_ARTIFACT"] = str(artifact)
    environment["RAF_FALSIFIER_SHA"] = expected
    environment["RAF_FALSIFIER_ID"] = fid
    try:
        completed = subprocess.run(
            ["bash", "--noprofile", "--norc", str(script)], cwd=workspace,
            env=environment, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=120, check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise GateError("FALSIFIER_EXECUTION_FAILED") from exc
    if completed.returncode != 0:
        raise GateError("FALSIFIER_REJECTED")
    if _git(workspace, "rev-parse", "--verify", "HEAD") != expected or _git(
            workspace, "status", "--porcelain", "--untracked-files=no"):
        raise GateError("POST_FALSIFIER_SOURCE_CHANGED")
    # Guard against falsifier deleting or swapping the target.
    artifact = _file_under(workspace, context["RAF_ARTIFACT_PATH"], MAX_ARTIFACT)
    script = _file_under(workspace, context["RAF_FALSIFIER_SCRIPT"], MAX_SCRIPT)
    if script_digest != _digest(script):
        raise GateError("FALSIFIER_CHANGED")
    record = {
        "schema": SCHEMA,
        "repository": repo,
        "source_commit_sha": expected,
        "run_id": int(run_id),
        "run_attempt": int(attempt),
        "run_url": "https://github.com/" + repo + "/actions/runs/" + run_id,
        "artifact_path": context["RAF_ARTIFACT_PATH"],
        "artifact_size": artifact.stat().st_size,
        "artifact_sha256": _digest(artifact),
        "falsifier_id": fid,
        "falsifier_path": context["RAF_FALSIFIER_SCRIPT"],
        "falsifier_script_sha256": script_digest,
        "falsifier_exit_code": 0,
        "falsifier_state": "PASS_SCOPED",
        "github_run_conclusion": "NOT_YET_ATTESTED",
        "independent_review": "NOT_RUN",
        "receipt_type": "PROVISIONAL_HOST_TEST",
        "claim_allowed": False,
        "promotion": "HOLD",
    }
    data = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    record["receipt_sha256"] = hashlib.sha256(data.encode("ascii")).hexdigest()
    return record


def main() -> int:
    try:
        record = issue_receipt(dict(os.environ))
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        _append_file(os.environ.get("GITHUB_OUTPUT", ""),
                     "receipt-sha256=" + record["receipt_sha256"] + "\n"
                     + "artifact-sha256=" + record["artifact_sha256"] + "\n"
                     + "source-sha=" + record["source_commit_sha"] + "\n")
        _append_file(os.environ.get("GITHUB_STEP_SUMMARY", ""),
                     "### RAFCODE provisional execution receipt (HOLD)\n\n"
                     + "| Source commit | Run | Falsifier | Artifact SHA256 | Receipt SHA256 |\n"
                     + "|---|---|---|---|---|\n"
                     + "| `" + record["source_commit_sha"] + "` | [run]("
                     + record["run_url"] + ") | `" + record["falsifier_id"]
                     + "` | `" + record["artifact_sha256"] + "` | `"
                     + record["receipt_sha256"] + "` |\n\n"
                     + "Host falsifier PASS_SCOPED; independent provider-run"
                     + " conclusion and review NOT_ATTESTED; CLAIM_ALLOWED=false.\n")
        print("RAFCODE_RECEIPT=" + serialized)
        return 0
    except (GateError, ValueError, OSError, subprocess.SubprocessError) as exc:
        # Fail closed, do not print source files or credentials.
        code = str(exc) if isinstance(exc, GateError) else "UNEXPECTED_HOST_FAILURE"
        print("RAFCODE_RECEIPT=BLOCKED reason=" + code, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
