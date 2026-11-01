"""Adversarial tests for the bounded authorship/CI separation gate."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from provenance.verify_attribution import check, git_blob_sha1

BASE = {
    "schema": "rafaelia.actions.attribution-snapshot/v2",
    "repository": "rafaelmeloreisnovo/actions",
    "upstream_repository": "gradle/actions",
    "observed_source_commit": "a" * 40,
    "github_actions_platform": "GITHUB_HOSTED_EXTERNAL_SERVICE_NOT_REPO_CODE",
    "whole_repository_original_authorship_claim": False,
    "exclusive_rights_proven": False,
    "release_allowed": False,
    "ci_pass_at_observed_head": False,
    "ci_evidence_state": "NO_WORKFLOW_RUN_RETURNED_FOR_OBSERVED_HEAD_OR_PR22_HEAD_AT_AUDIT",
    "external_authorities": [
        {"role": "PLATFORM_PROVIDER"},
        {"role": "THIRD_PARTY_ACTION_DEPENDENCY"},
        {"role": "UPSTREAM_PROJECT"},
    ],
}


class AttributionGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        p = self.root / "local" / "kernel.c"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"int original_candidate;\n")
        self.data = copy.deepcopy(BASE)
        self.data["files"] = [{
            "path": "local/kernel.c",
            "blob": git_blob_sha1(p.read_bytes()),
            "origin": "LOCAL_ADDED_CANDIDATE",
            "provenance": "local commit and path; rights unverified",
            "rights": "HOLDER_ATTESTATION_PENDING",
        }]

    def assertBlocked(self, phrase):
        issues = check(self.data, self.root)
        self.assertTrue(any(phrase in issue for issue in issues), issues)

    def test_scoped_positive_not_legal_clearance(self):
        self.assertEqual([], check(self.data, self.root))
        self.assertFalse(self.data["release_allowed"])
        self.assertFalse(self.data["ci_pass_at_observed_head"])

    def test_blob_tampering_fails(self):
        (self.root / "local/kernel.c").write_bytes(b"changed")
        self.assertBlocked("blob drift")

    def test_fork_wide_authorship_claim_fails(self):
        self.data["whole_repository_original_authorship_claim"] = True
        self.assertBlocked("whole_repository_original_authorship_claim")

    def test_false_ci_pass_fails(self):
        self.data["ci_pass_at_observed_head"] = True
        self.assertBlocked("ci_pass_at_observed_head")

    def test_promotion_or_rights_claim_fails(self):
        self.data["release_allowed"] = True
        self.data["exclusive_rights_proven"] = True
        self.assertBlocked("release_allowed")
        self.assertBlocked("exclusive_rights_proven")

    def test_provider_misattribution_fails(self):
        self.data["github_actions_platform"] = "RAFAELIA_CORE"
        self.assertBlocked("platform conflated")

    def test_path_traversal_rejected(self):
        self.data["files"][0]["path"] = "../LICENSE"
        self.assertBlocked("unsafe path")

    def test_symlink_rejected(self):
        (self.root / "local/kernel.c").unlink()
        (self.root / "local/kernel.c").symlink_to(self.root / "not-a-source")
        self.assertBlocked("missing or linked file")

    def test_duplicate_path_rejected(self):
        self.data["files"].append(copy.deepcopy(self.data["files"][0]))
        self.assertBlocked("duplicate path")

    def test_local_reuse_requires_equal_blob_and_ancestor(self):
        p = self.root / "local" / "copy.c"
        p.write_bytes(b"int original_candidate;\n")
        reuse = dict(self.data["files"][0], path="local/copy.c",
                     origin="LOCAL_REUSE_OF_LOCAL_CANDIDATE",
                     same_blob_as="local/kernel.c")
        self.data["files"].append(reuse)
        self.assertEqual([], check(self.data, self.root))
        reuse["same_blob_as"] = "local/missing.c"
        self.assertBlocked("same-blob provenance invalid")

    def test_unclassified_ownership_rejected(self):
        self.data["files"][0]["origin"] = "EXCLUSIVE_OWNER"
        self.assertBlocked("unapproved origin")


if __name__ == "__main__":
    unittest.main()
