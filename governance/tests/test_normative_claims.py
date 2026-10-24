"""Hosted documentary claim gate: checks flags, never certifies RAFAELIA."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "governance" / "normative_claim_state.v1.json"
POLICY = ROOT / "governance" / "NORMATIVE_CLAIM_POLICY_V1.md"

def check_policy(record):
    errors = []
    if record.get("schema") != "rafaelia.normative-claim-state/v1":
        errors.append("invalid schema")
    if record.get("authority") != "human-review-required":
        errors.append("human authority not retained")
    for forbidden in ("claims_are_automatically_promoted",
                      "full_conformity_claim_allowed",
                      "certification_claim_allowed"):
        if record.get(forbidden) is not False:
            errors.append("unauthorized normative claim: " + forbidden)
    if record.get("certification_evidence_status") != "TOKEN_VAZIO_NOT_OBSERVED":
        errors.append("unverified certificate promoted")
    if record.get("conformity_assessment_evidence_status") != "TOKEN_VAZIO_NOT_OBSERVED":
        errors.append("unverified conformity promoted")
    return errors

class NormativeClaimGate(unittest.TestCase):
    def test_scoped_policy_is_fail_closed(self):
        self.assertEqual([],check_policy(json.loads(STATE.read_text(encoding="utf-8"))))

    def test_no_certification_without_external_proof(self):
        base = json.loads(STATE.read_text(encoding="utf-8"))
        for flag in ("certification_claim_allowed","full_conformity_claim_allowed",
                     "claims_are_automatically_promoted"):
            changed = dict(base, **{flag:True})
            with self.subTest(flag=flag):
                self.assertTrue(check_policy(changed))

    def test_missing_or_invented_evidence_rejected(self):
        base = json.loads(STATE.read_text(encoding="utf-8"))
        for status in (None, "CERTIFIED", "PASS", "0"):
            with self.subTest(status=status):
                self.assertTrue(check_policy(dict(base,certification_evidence_status=status)))

    def test_human_wording_and_external_proof_route_exist(self):
        text = POLICY.read_text(encoding="utf-8")
        for marker in ("REFERENCE_ONLY","TESTED_SCOPED","CERTIFICATION_VERIFIED_SCOPED",
                       "organismo certificador","https://www.iso.org/certification.html",
                       "TOKEN_VAZIO_NOT_OBSERVED"):
            with self.subTest(marker=marker):
                self.assertIn(marker,text)

if __name__ == "__main__":
    unittest.main()
