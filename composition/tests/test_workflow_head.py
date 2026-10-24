"""Host-only source contract: independent first-party workflows must bind the PR HEAD."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class WorkflowHeadContracts(unittest.TestCase):
    def test_rafcode_ref_is_not_pr_merge_ref(self):
        data = (ROOT / ".github/workflows/rafcode-l0.yml").read_text(encoding="utf-8")
        self.assertIn("github.event.pull_request.head.sha || github.sha", data)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_SHA"', data)
        self.assertNotIn('git fetch --depth=1 origin "$GITHUB_REF"', data)
        self.assertIn('protocol.version=2 fetch --no-tags --depth=1 origin "$EXPECTED_SOURCE_SHA"', data)
        self.assertIn("contents: read", data)
        self.assertNotIn("contents: write", data)

    def test_new_rights_lane_keeps_release_blocked(self):
        data = (ROOT / ".github/workflows/ci-rafaelia-rights.yml").read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", data)
        self.assertIn("github.event.pull_request.head.sha || github.sha", data)
        self.assertIn("-fsanitize=address,undefined", data)
        self.assertIn("release_authorized=0", data)
