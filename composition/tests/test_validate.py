"""Adversarial checks: malformed contract must not be accepted."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "composition"))
from validate import validate  # noqa: E402

DATA = json.loads((ROOT / "composition" / "next_steps.v1.json").read_text(encoding="utf-8"))


class CompositionContractTests(unittest.TestCase):
    def test_current_contract(self):
        self.assertEqual([], validate(DATA))

    def test_claim_cannot_be_promoted(self):
        altered = copy.deepcopy(DATA)
        altered["claim_allowed"] = True
        self.assertTrue(validate(altered))

    def test_lane_evidence_cannot_be_inferred(self):
        altered = copy.deepcopy(DATA)
        altered["lanes"][0]["current_evidence"] = "PASS"
        self.assertTrue(validate(altered))

    def test_missing_source_route(self):
        altered = copy.deepcopy(DATA)
        altered["lanes"][0]["source_paths"] = ["freestanding/not-real/source.c"]
        self.assertTrue(validate(altered))

    def test_step_gap_must_be_typed(self):
        altered = copy.deepcopy(DATA)
        altered["steps"][0]["gap"] = "0"
        self.assertTrue(validate(altered))

    def test_missing_dependency_rejected(self):
        altered = copy.deepcopy(DATA)
        altered["steps"][0]["depends_on"] = ["P0-99"]
        self.assertTrue(validate(altered))

    def test_cycle_rejected(self):
        altered = copy.deepcopy(DATA)
        altered["steps"][1]["depends_on"] = ["P0-03"]
        self.assertTrue(validate(altered))

    def test_no_finished_state_without_external_evidence(self):
        altered = copy.deepcopy(DATA)
        altered["steps"][0]["state"] = "PASS"
        self.assertTrue(validate(altered))


if __name__ == "__main__":
    unittest.main()
