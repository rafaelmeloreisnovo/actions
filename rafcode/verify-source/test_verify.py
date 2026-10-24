"""Exercise the actual shell adapter against disposable Git repositories."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("verify.sh")


class SourceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.root / "source.c").write_text("original\n")
        self.git("add", "source.c")
        self.git("commit", "-qm", "fixture")
        self.sha = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              text=True, capture_output=True)

    def run_gate(self, sha, *, cwd=None):
        output = self.root / "gate-output"
        output.write_text("")
        env = dict(os.environ, RAF_EXPECTED_SHA=sha, GITHUB_OUTPUT=str(output))
        run = subprocess.run(["bash", str(SCRIPT)], cwd=cwd or self.root,
                             env=env, text=True, capture_output=True)
        return run, output.read_text()

    def reject(self, sha, reason, **kwargs):
        run, output = self.run_gate(sha, **kwargs)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(reason, run.stderr)
        self.assertEqual(output, "")
        self.assertNotIn("PASS_SCOPED", run.stdout)

    def test_exact_clean_commit(self):
        run, output = self.run_gate(self.sha)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(output, f"source-sha={self.sha}\n")

    def test_wrong_commit(self):
        self.reject("0" * 40, "source_sha_mismatch")

    def test_empty_short_uppercase_and_injection(self):
        for sha in ("", self.sha[:7], "A" * 40, "$(touch injected)", self.sha + "\n"):
            with self.subTest(sha=sha):
                self.reject(sha, "invalid_expected_sha")
        self.assertFalse((self.root / "injected").exists())

    def test_unstaged_change(self):
        (self.root / "source.c").write_text("changed\n")
        self.reject(self.sha, "modified_worktree")

    def test_staged_change(self):
        (self.root / "source.c").write_text("changed\n")
        self.git("add", "source.c")
        self.reject(self.sha, "modified_index")

    def test_deleted_tracked_source(self):
        (self.root / "source.c").unlink()
        self.reject(self.sha, "modified_worktree")

    def test_non_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            self.reject(self.sha, "missing_git_head", cwd=empty)

    def test_second_commit_is_not_first_commit_evidence(self):
        (self.root / "source.c").write_text("successor\n")
        self.git("commit", "-qam", "successor")
        self.reject(self.sha, "source_sha_mismatch")
        run, _ = self.run_gate(self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
