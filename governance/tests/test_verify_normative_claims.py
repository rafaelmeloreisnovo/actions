"""Negative and mutation-style tests for claim boundaries (no ISO audit)."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "governance"))
from verify_normative_claims import (  # noqa: E402
    DuplicateKeyError, check_file, parse_manifest, validate_manifest,
)

MANIFEST = ROOT / "governance" / "normative_claim_state.v1.json"


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = parse_manifest(MANIFEST.read_text(encoding="utf-8"))

    def test_known_manifest_is_documentary_only(self):
        self.assertEqual(validate_manifest(self.base), [])
        self.assertEqual(check_file(MANIFEST), [])

    def test_certification_promotion_cannot_be_enabled(self):
        for key in ("certification_claim_allowed", "full_conformity_claim_allowed",
                    "claims_are_automatically_promoted"):
            with self.subTest(key=key):
                changed = dict(self.base, **{key: True})
                self.assertTrue(validate_manifest(changed))

    def test_truthy_string_does_not_count_as_false(self):
        self.assertTrue(validate_manifest(dict(self.base, certification_claim_allowed="false")))

    def test_reference_only_requires_explicit_reference_flag(self):
        self.assertTrue(validate_manifest(dict(self.base, best_practices_reference_allowed=False)))

    def test_receipt_required_flag_cannot_be_silently_removed(self):
        self.assertTrue(validate_manifest(dict(self.base, scoped_implementation_claim_requires_receipt=False)))

    def test_status_unknown_is_not_numeric_zero(self):
        for value in (0, "0", "PASS", "CERTIFIED", None, ""):
            with self.subTest(value=value):
                self.assertTrue(validate_manifest(dict(self.base, certification_evidence_status=value)))

    def test_assessed_conformity_cannot_be_inferred(self):
        self.assertTrue(validate_manifest(dict(self.base, conformity_assessment_evidence_status="PASS")))

    def test_required_proof_is_not_silently_erased(self):
        altered = copy.deepcopy(self.base)
        altered["required_for_certification_claim"].remove("certified_scope")
        self.assertTrue(validate_manifest(altered))

    def test_duplicate_required_items_are_rejected(self):
        altered = copy.deepcopy(self.base)
        altered["required_for_certification_claim"].append("certified_scope")
        self.assertTrue(validate_manifest(altered))

    def test_duplicate_manifest_json_keys_fail_closed(self):
        with self.assertRaises(DuplicateKeyError):
            parse_manifest('{"certification_claim_allowed":false,"certification_claim_allowed":true}')

    def test_unknown_or_missing_field_rejected(self):
        altered = copy.deepcopy(self.base)
        altered.pop("repo")
        self.assertTrue(validate_manifest(altered))
        altered = dict(self.base, invented_certification=True)
        self.assertTrue(validate_manifest(altered))

    def test_wrong_repo_or_authority_rejected(self):
        self.assertTrue(validate_manifest(dict(self.base, repo="unknown/actions")))
        self.assertTrue(validate_manifest(dict(self.base, authority="bot")))

    def test_non_object_rejected(self):
        self.assertTrue(validate_manifest(None))
        with self.assertRaises(ValueError):
            parse_manifest('[1,2,3]')

    def test_blank_provenance_rejected(self):
        for key in ("observed_date", "origin", "note"):
            with self.subTest(key=key):
                self.assertTrue(validate_manifest(dict(self.base, **{key: " "}))


if __name__ == "__main__":
    unittest.main()
