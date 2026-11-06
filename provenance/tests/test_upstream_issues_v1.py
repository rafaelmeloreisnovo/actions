"""Negative tests for the bounded upstream issue routing graph."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("upstream_routes", ROOT / "provenance/verify_upstream_issues_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
DATA = json.loads((ROOT / "provenance/upstream_issues_roadmap.v1.json").read_text())


class UpstreamRouteTests(unittest.TestCase):
    def test_bounded_manifest(self):
        self.assertEqual([], MOD.validate(DATA))

    def test_cannot_claim_ci_pass(self):
        modified = copy.deepcopy(DATA)
        modified["gate_policy"]["provider_check_state"] = "PASS"
        self.assertTrue(MOD.validate(modified))

    def test_cannot_release_unverified_patch(self):
        modified = copy.deepcopy(DATA)
        modified["issues"][0]["release_allowed"] = True
        self.assertTrue(MOD.validate(modified))

    def test_cannot_misroute_closed_source_producer(self):
        modified = copy.deepcopy(DATA)
        modified["typed_edges"] = [x for x in modified["typed_edges"] if x["from"] != "gradle/actions#316"]
        self.assertTrue(MOD.validate(modified))

    def test_cannot_fabricate_producer_for_1088(self):
        modified = copy.deepcopy(DATA)
        modified["typed_edges"] = [x for x in modified["typed_edges"] if x["from"] != "gradle/actions#1088"]
        self.assertTrue(MOD.validate(modified))

    def test_cannot_rebase_scoped_patch_to_fork_main(self):
        modified = copy.deepcopy(DATA)
        modified["issues"][1]["patch_base"] = modified["fork_main_sha"]
        self.assertTrue(MOD.validate(modified))

    def test_no_deadline_invention(self):
        modified = copy.deepcopy(DATA)
        modified["issues"][0]["hard_deadline"] = "2026-11-09"
        self.assertTrue(MOD.validate(modified))

    def test_no_collapsed_issues(self):
        modified = copy.deepcopy(DATA)
        modified["issues"] = modified["issues"][:-1]
        self.assertTrue(MOD.validate(modified))


if __name__ == "__main__":
    unittest.main()
