#!/usr/bin/env python3
"""Post-run provider readback of provisional RAFCODE receipts (read-only, hosted)."""
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

SCHEMA = "rafaelia.rafcode.host-execution-receipt.v1"
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
REPO = re.compile(r"rafaelmeloreisnovo/[A-Za-z0-9_.-]+\Z")
ALLOWED_STEPS = {
    "Author-owned action — run, artifact, falsifier SHA256 receipt",
    "Pilot hosted artifact+falsifier receipt from candidate owned Action",
    "RAFCODE provisional run/artifact/falsifier receipt — same Actions core",
    "Author-owned action — provisional SHA256 and falsifier execution receipt",
}
EXPECTED = {
    "schema", "repository", "source_commit_sha", "run_id", "run_attempt",
    "run_url", "artifact_path", "artifact_size", "artifact_sha256",
    "falsifier_id", "falsifier_path", "falsifier_script_sha256",
    "falsifier_exit_code", "falsifier_state", "github_run_conclusion",
    "independent_review", "receipt_type", "claim_allowed", "promotion",
    "receipt_sha256",
}


class VerifyError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, url):
        raise VerifyError("PROVIDER_REDIRECT_DENIED")


def provider_json(path):
    if not path.startswith("/repos/rafaelmeloreisnovo/") or ".." in path or "\\" in path:
        raise VerifyError("PROVIDER_PATH_DENIED")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "RAFCODE-evidence-auditor/1"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com" + path,
                                     headers=headers, method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=12) as response:
            data = response.read(1024 * 1024 + 1)
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise VerifyError("PROVIDER_READ_UNAVAILABLE") from exc
    if len(data) > 1024 * 1024:
        raise VerifyError("PROVIDER_TOO_LARGE")
    try:
        return json.loads(data)
    except ValueError as exc:
        raise VerifyError("PROVIDER_JSON_UNTRUSTED") from exc


def source_path(name):
    if (not isinstance(name, str) or not name or len(name) > 240
            or name.startswith("/") or any(
                not re.fullmatch(r"[A-Za-z0-9._-]+", part)
                for part in name.split("/"))):
        raise VerifyError("SOURCE_PATH_UNTRUSTED")
    return "/".join(urllib.parse.quote(part, safe="") for part in name.split("/"))


def validate(record):
    if not isinstance(record, dict) or set(record) != EXPECTED:
        raise VerifyError("RECEIPT_SCHEMA_MISMATCH")
    if (record["schema"] != SCHEMA or record["receipt_type"] != "PROVISIONAL_HOST_TEST"
            or record["falsifier_state"] != "PASS_SCOPED"
            or type(record["falsifier_exit_code"]) is not int or record["falsifier_exit_code"] != 0
            or record["github_run_conclusion"] != "NOT_YET_ATTESTED"
            or record["independent_review"] != "NOT_RUN"
            or record["claim_allowed"] is not False or record["promotion"] != "HOLD"):
        raise VerifyError("RECEIPT_FALSE_PROMOTION")
    if (not isinstance(record["repository"], str) or not REPO.fullmatch(record["repository"])
            or not isinstance(record["source_commit_sha"], str) or not HEX40.fullmatch(record["source_commit_sha"])
            or not isinstance(record["artifact_sha256"], str) or not HEX64.fullmatch(record["artifact_sha256"])
            or not isinstance(record["falsifier_script_sha256"], str) or not HEX64.fullmatch(record["falsifier_script_sha256"])
            or type(record["run_id"]) is not int or record["run_id"] < 1
            or type(record["run_attempt"]) is not int or record["run_attempt"] < 1
            or type(record["artifact_size"]) is not int or not 1 <= record["artifact_size"] <= 128 * 1024 * 1024):
        raise VerifyError("RECEIPT_IDENTITY_INVALID")
    source_path(record["artifact_path"])
    source_path(record["falsifier_path"])
    if record["run_url"] != ("https://github.com/" + record["repository"] +
                             "/actions/runs/" + str(record["run_id"])):
        raise VerifyError("RUN_URL_FORGED")
    expected = hashlib.sha256(json.dumps({k: v for k, v in record.items()
        if k != "receipt_sha256"}, ensure_ascii=True, sort_keys=True,
        separators=(",", ":")).encode("ascii")).hexdigest()
    if record["receipt_sha256"] != expected:
        raise VerifyError("RECEIPT_DIGEST_MISMATCH")


def verify_blob(data, sha, size=None):
    if not isinstance(data, dict) or data.get("type") != "file" or data.get("encoding") != "base64":
        return False
    text = data.get("content")
    if not isinstance(text, str) or len(text) > 1400000:
        return False
    try:
        raw = base64.b64decode(text.replace("\n", "").replace("\r", ""), validate=True)
    except (ValueError, binascii.Error):
        return False
    if len(raw) > 1024 * 1024 or data.get("size") != len(raw):
        return False
    if size is not None and len(raw) != size:
        return False
    blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    return data.get("sha") == blob_sha and hashlib.sha256(raw).hexdigest() == sha


def verify(record, fetch=provider_json):
    validate(record)
    repo = record["repository"]
    runid = record["run_id"]
    prefix = "/repos/" + repo
    run = fetch(prefix + "/actions/runs/" + str(runid))
    if (not isinstance(run, dict) or run.get("id") != runid or
            run.get("head_sha") != record["source_commit_sha"] or
            run.get("run_attempt") != record["run_attempt"] or
            run.get("status") != "completed" or run.get("conclusion") != "success"):
        raise VerifyError("PROVIDER_RUN_NOT_VERIFIED")
    jobs = fetch(prefix + "/actions/runs/" + str(runid) + "/jobs?per_page=100")
    valid = []
    if not isinstance(jobs, dict) or not isinstance(jobs.get("jobs"), list):
        raise VerifyError("PROVIDER_JOBS_MISSING")
    for job in jobs["jobs"]:
        if not isinstance(job, dict) or job.get("conclusion") != "success":
            continue
        for step in job.get("steps", []):
            if (isinstance(step, dict) and step.get("name") in ALLOWED_STEPS
                    and step.get("status") == "completed" and step.get("conclusion") == "success"):
                valid.append(job.get("id"))
    if len(valid) != 1:
        raise VerifyError("PROVIDER_ACTION_STEP_NOT_VERIFIED")
    artifact = fetch(prefix + "/contents/" + source_path(record["artifact_path"])
                     + "?ref=" + record["source_commit_sha"])
    if not verify_blob(artifact, record["artifact_sha256"], record["artifact_size"]):
        raise VerifyError("ARTIFACT_BYTES_DISAGREE")
    script = fetch(prefix + "/contents/" + source_path(record["falsifier_path"])
                   + "?ref=" + record["source_commit_sha"])
    if not verify_blob(script, record["falsifier_script_sha256"]):
        raise VerifyError("FALSIFIER_BYTES_DISAGREE")
    output = {
        "schema": "rafaelia.rafcode.provider-run-audit/v1",
        "repository": repo,
        "commit_sha": record["source_commit_sha"],
        "run_id": runid,
        "provider_job_id": valid[0],
        "provider_execution": "SUCCESS_VERIFIED_SCOPED",
        "artifact_sha256": record["artifact_sha256"],
        "falsifier_script_sha256": record["falsifier_script_sha256"],
        "receipt_sha256": record["receipt_sha256"],
        "domain_runtime": "NOT_PROVEN",
        "independent_review": "NOT_RUN",
        "claim_allowed": False,
        "promotion": "HOLD",
    }
    output["audit_sha256"] = hashlib.sha256(json.dumps(output, ensure_ascii=True,
        sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return output


def main():
    if len(sys.argv) != 2:
        print("Usage: provider_verify.py receipt.json", file=sys.stderr)
        return 2
    try:
        receipt = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        audit = verify(receipt)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"state": "BLOCKED",
                          "reason": str(exc) if isinstance(exc, VerifyError) else "VERIFIER_EXCEPTION",
                          "claim_allowed": False}), file=sys.stderr)
        return 2
    print(json.dumps(audit, sort_keys=True, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
