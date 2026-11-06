"""Adversarial bounded checks. No GitHub provider or copyright verdict."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("license_scopes", ROOT / "provenance/verify_license_scopes_v1.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
MANIFEST = json.loads((ROOT / "provenance/license_scopes.v1.json").read_text(encoding="utf-8"))


class LicenseScopesTests(unittest.TestCase):
    def check(self, data):
        return MODULE.check(data, ROOT)

    def test_canonical_selected_scope_passes(self):
        self.assertEqual([], self.check(MANIFEST))

    def test_broadening_proof_without_evidence_fails(self):
        for field in MODULE.ZERO_GRANT_FIELDS:
            with self.subTest(field=field):
                data = copy.deepcopy(MANIFEST)
                data[field] = True
                self.assertTrue(self.check(data))

    def test_local_scope_cannot_be_blindly_relicensed_as_upstream(self):
        data = copy.deepcopy(MANIFEST)
        rec = next(x for x in data["paths"] if x["id"] == "local-kernel4")
        rec["category"] = "INHERITED"
        rec["license_route"] = "LICENSE"
        self.assertTrue(any("boundary" in e or "origin" in e
                            for e in self.check(data)))

    def test_upstream_root_notice_cannot_be_overwritten(self):
        data = copy.deepcopy(MANIFEST)
        data["protected_root_license_blob"] = "0" * 40
        self.assertTrue(any("root license" in e for e in self.check(data)))

    def test_duplicate_scope_and_extra_blob_falsifier(self):
        data = copy.deepcopy(MANIFEST)
        data["paths"].append(copy.deepcopy(data["paths"][0]))
        self.assertTrue(self.check(data))
        data = copy.deepcopy(MANIFEST)
        data["examples"][0]["blob"] = "0" * 40
        self.assertTrue(any("byte drift" in e for e in self.check(data)))

    def test_untrusted_path_and_missing_source_are_not_silent(self):
        data = copy.deepcopy(MANIFEST)
        data["paths"][0]["path"] = "../LICENSE"
        self.assertTrue(any("unsafe" in e for e in self.check(data)))
        data = copy.deepcopy(MANIFEST)
        data["examples"][0]["path"] = "missing/source.c"
        self.assertTrue(self.check(data))

    def test_reuse_is_not_a_second_original_author(self):
        data = copy.deepcopy(MANIFEST)
        data["examples"][-1]["same_blob_as"] = "freestanding/kernel4/kernel4.c"
        self.assertTrue(any("duplicate-source identity" in e for e in self.check(data)))

    def test_unknown_license_holder_stays_empty(self):
        data = copy.deepcopy(MANIFEST)
        data["paths"][-1]["holder_verified"] = True
        self.assertTrue(any("unauthorized promotion" in e for e in self.check(data)))
        data = copy.deepcopy(MANIFEST)
        data["authored_code_grant_state"] = "MIT_SELECTED"
        self.assertTrue(any("fabricated" in e for e in self.check(data)))

    def test_no_whole_fork_authorship_by_presentation(self):
        self.assertFalse(MANIFEST["whole_repo_authorial"])
        self.assertFalse(MANIFEST["new_license_grant_issued"])
        self.assertEqual("gradle/actions", MANIFEST["upstream"])
        self.assertEqual("LICENSE", MANIFEST["root_license"])

if __name__ == "__main__":
    unittest.main()
