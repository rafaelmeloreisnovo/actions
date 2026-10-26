"""Tests execute real hosted Git+Bash but never a remote provider or phone."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).with_name("issue_receipt.py")
spec = importlib.util.spec_from_file_location("receipt", MODULE)
receipt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt)


class HostedReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cmd("git", "init", "-q")
        self.cmd("git", "config", "user.name", "RAFCODE Fixture")
        self.cmd("git", "config", "user.email", "ci@example.invalid")
        (self.root / "fixture.bin").write_bytes(b"sample-for-sha256\n")
        (self.root / "falsify.sh").write_text(
            "set -euo pipefail\n"
            'test "$RAF_FALSIFIER_ID" = FALSIFIER_FIXTURE\n'
            'test -s "$RAF_FALSIFIER_ARTIFACT"\n'
            'test "$RAF_FALSIFIER_SHA" = "' + "0" * 40 + '" || true\n'
        )
        self.cmd("git", "add", "fixture.bin", "falsify.sh")
        self.cmd("git", "commit", "-qm", "fixture")
        self.sha = self.cmd("git", "rev-parse", "HEAD").stdout.strip()
        self.context = dict(os.environ)
        self.context.update(GITHUB_WORKSPACE=str(self.root),
                            GITHUB_REPOSITORY="rafaelmeloreisnovo/BOOTSTRAPsys",
                            GITHUB_RUN_ID="40123456789",
                            GITHUB_RUN_ATTEMPT="1",
                            RAF_EXPECTED_SHA=self.sha,
                            RAF_ARTIFACT_PATH="fixture.bin",
                            RAF_FALSIFIER_SCRIPT="falsify.sh",
                            RAF_FALSIFIER_ID="FALSIFIER_FIXTURE")

    def cmd(self, *args):
        return subprocess.run(args, cwd=self.root, text=True,
                              capture_output=True, check=True)

    def get(self, **replacements):
        return receipt.issue_receipt({**self.context, **replacements})

    def fail(self, marker, **replacements):
        with self.assertRaisesRegex(receipt.GateError, marker):
            self.get(**replacements)

    def test_real_gate_and_sha_contract(self):
        result = self.get()
        self.assertEqual(result["source_commit_sha"], self.sha)
        self.assertEqual(result["artifact_sha256"],
                         receipt.hashlib.sha256(b"sample-for-sha256\n").hexdigest())
        self.assertEqual(result["run_id"], 40123456789)
        self.assertEqual(result["falsifier_state"], "PASS_SCOPED")
        self.assertEqual(result["receipt_type"], "PROVISIONAL_HOST_TEST")
        self.assertFalse(result["claim_allowed"])
        self.assertEqual(self.get(), result)

    def test_wrong_sha_and_bad_run_id(self):
        self.fail("HEAD_DRIFT", RAF_EXPECTED_SHA="0" * 40)
        self.fail("CONTEXT_MALFORMED", GITHUB_RUN_ID="$(touch pwn)")

    def test_path_traversal_and_missing(self):
        self.fail("UNSAFE_RELATIVE_PATH", RAF_ARTIFACT_PATH="../outside")
        self.fail("REGULAR_FILE_REQUIRED", RAF_ARTIFACT_PATH="nonexistent.bin")

    def test_symlink_artifact_rejected(self):
        (self.root / "link").symlink_to(self.root / "fixture.bin")
        self.fail("SYMLINK_DENIED", RAF_ARTIFACT_PATH="link")

    def test_falsifier_rejection_not_claimed(self):
        (self.root / "falsify.sh").write_text("exit 1\n")
        self.fail("TRACKED_SOURCE_DIRTY")

    def test_falsifier_rejects_with_clean_committed_source(self):
        (self.root / "falsify.sh").write_text("exit 17\n")
        self.cmd("git", "add", ".")
        self.cmd("git", "commit", "-qm", "negative")
        self.fail("FALSIFIER_REJECTED",
                  RAF_EXPECTED_SHA=self.cmd("git", "rev-parse", "HEAD").stdout.strip())

    def test_dirty_tracked_artifact_rejected(self):
        (self.root / "fixture.bin").write_bytes(b"changed")
        self.fail("TRACKED_SOURCE_DIRTY")

    def test_invalid_falsifier_identity(self):
        self.fail("CONTEXT_MALFORMED", RAF_FALSIFIER_ID="test-unsafe")

    def test_falsifier_does_not_inherit_credential(self):
        (self.root / "falsify.sh").write_text(
            'test -z "${GITHUB_TOKEN:-}" && test -z "${GH_TOKEN:-}"\n')
        self.cmd("git", "add", "falsify.sh")
        self.cmd("git", "commit", "-qm", "test isolated env")
        current = self.cmd("git", "rev-parse", "HEAD").stdout.strip()
        data = self.get(RAF_EXPECTED_SHA=current, GITHUB_TOKEN="secret",
                        GH_TOKEN="secret")
        self.assertEqual(data["falsifier_state"], "PASS_SCOPED")


if __name__ == "__main__":
    unittest.main()
