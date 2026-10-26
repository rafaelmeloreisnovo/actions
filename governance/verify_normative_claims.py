"""RAFAELIA documentary gate v1 (HOST tool, never a certification authority).

This gate validates one fail-closed, versioned statement of *unverified*
certification/conformity evidence. It cannot inspect a certification registry,
audit an ISO system, or infer NIST approval. No external services are called.
"""
import json
from pathlib import Path
import sys

EXPECTED_SCHEMA = "rafaelia.normative-claim-state/v1"
UNKNOWN = "TOKEN_VAZIO_NOT_OBSERVED"
REQUIRED_CERT_FIELDS = frozenset({
    "certificate_identifier", "certificate_holder", "standard_edition",
    "certification_body", "certified_scope", "validity_period",
    "authenticated_registry_or_issuer_check", "accreditation_if_claimed",
})
REQUIRED_KEYS = frozenset({
    "schema", "observed_date", "authority", "repo",
    "claims_are_automatically_promoted", "best_practices_reference_allowed",
    "scoped_implementation_claim_requires_receipt", "full_conformity_claim_allowed",
    "certification_claim_allowed", "certification_evidence_status",
    "conformity_assessment_evidence_status", "origin",
    "required_for_certification_claim", "note",
})


class DuplicateKeyError(ValueError):
    """Avoid quietly accepting the last value of duplicated JSON claims."""


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate key: " + key)
        result[key] = value
    return result


def parse_manifest(raw):
    result = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(result, dict):
        raise ValueError("manifest must be a JSON object")
    return result


def validate_manifest(item):
    """Return typed errors; an empty result means DOCUMENT_ONLY_ACCEPTED."""
    if not isinstance(item, dict):
        return ["INVALID_MANIFEST_TYPE"]
    failures = []
    missing = REQUIRED_KEYS.difference(item)
    extra = set(item).difference(REQUIRED_KEYS)
    if missing:
        failures.append("MISSING_FIELDS:" + ",".join(sorted(missing)))
    if extra:
        failures.append("UNKNOWN_FIELDS:" + ",".join(sorted(extra)))
    if item.get("schema") != EXPECTED_SCHEMA:
        failures.append("UNSUPPORTED_SCHEMA")
    if item.get("repo") != "rafaelmeloreisnovo/actions":
        failures.append("WRONG_REPOSITORY")
    if item.get("authority") != "human-review-required":
        failures.append("REVIEW_AUTHORITY_UNRESOLVED")
    for field in (
        "claims_are_automatically_promoted", "full_conformity_claim_allowed",
        "certification_claim_allowed",
    ):
        if item.get(field) is not False:
            failures.append("UNAUTHORIZED_CLAIM:" + field)
    for field in (
        "best_practices_reference_allowed",
        "scoped_implementation_claim_requires_receipt",
    ):
        if item.get(field) is not True:
            failures.append("INVALID_CONTROL_FLAG:" + field)
    for field in (
        "certification_evidence_status", "conformity_assessment_evidence_status",
    ):
        if item.get(field) != UNKNOWN:
            failures.append("UNVERIFIED_EVIDENCE_PROMOTED:" + field)
    items = item.get("required_for_certification_claim")
    if not isinstance(items, list) or any(not isinstance(x, str) for x in items):
        failures.append("INVALID_CERT_REQUIRED_FIELDS")
    elif len(items) != len(set(items)) or set(items) != REQUIRED_CERT_FIELDS:
        failures.append("ALTERED_CERT_REQUIRED_FIELDS")
    for field in ("observed_date", "origin", "note"):
        val = item.get(field)
        if not isinstance(val, str) or not val.strip():
            failures.append("EMPTY_TRACE_FIELD:" + field)
    return failures


def check_file(path):
    try:
        data = parse_manifest(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return ["MANIFEST_READ_OR_PARSE_ERROR:" + str(exc)]
    return validate_manifest(data)


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "governance" / "normative_claim_state.v1.json"
    errors = check_file(path)
    if errors:
        for error in errors:
            print("BLOCKED:", error, file=sys.stderr)
        return 1
    print("DOCUMENT_ONLY_ACCEPTED; CERTIFICATION=NOT_VERIFIED; FULL_CONFORMITY=NOT_CLAIMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
