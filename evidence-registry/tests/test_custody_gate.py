"""RAFAELIA custody falsifiers; no outbound network and no provider write."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
COLLECT = ROOT / "evidence-registry" / "collect.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "evidence-registry.yml"
ALLOWED = ROOT / "evidence-registry" / "allowed_hosts.v1.txt"


class CustodyRules(unittest.TestCase):
    def test_writer_does_not_update_main_or_delete_refs(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('git push origin "HEAD:refs/heads/$branch"', source)
        self.assertIn("gh pr create --draft --base main", source)
        self.assertIn("pull-requests: write", source)
        self.assertIn("needs: [collect]", source)
        self.assertNotIn("git push origin HEAD:main", source)
        self.assertNotIn("git push --force", source)
        self.assertNotIn("git push -f", source)
        self.assertNotIn("git push origin --delete", source)
        self.assertNotIn("gh pr merge", source)

    def test_partial_and_redirects_are_not_evidence(self):
        # All curl invocations use a fake executable. No network access.
        mock = """#!/bin/sh
body=''
headers=''
previous=''
for part in "$@"; do
  case "$previous" in
    -o) body="$part" ;;
    -D) headers="$part" ;;
  esac
  previous="$part"
done
printf 'untrusted partial data' > "$body"
printf 'HTTP/1.1 %s\n' "$MOCK_STATUS" > "$headers"
printf '%s\ttext/plain\thttps://openai.com/news/' "$MOCK_STATUS"
exit "$MOCK_EXIT"
"""
        with tempfile.TemporaryDirectory(prefix="raf-custody-") as d:
            p = Path(d)
            curl = p / "curl"
            curl.write_text(mock, encoding="utf-8")
            curl.chmod(0o755)
            inp = p / "sources.tsv"
            inp.write_text("OpenAI\tprimary\thttps://openai.com/news/\n", encoding="utf-8")
            for status, code in (("302", "0"), ("200", "18")):
                with self.subTest(http=status, exit=code):
                    out = p / ("evidence-" + status)
                    env = dict(os.environ,
                               PATH=str(p) + os.pathsep + os.environ["PATH"],
                               RA_HOSTS_FILE=str(ALLOWED),
                               MOCK_STATUS=status,
                               MOCK_EXIT=code)
                    completed = subprocess.run(
                        ["bash", str(COLLECT), str(inp), str(out)],
                        cwd=ROOT, env=env, capture_output=True, text=True)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    records = [json.loads(line) for line in
                               (out / "latest-ledger.jsonl").read_text().splitlines()]
                    self.assertEqual(len(records), 1)
                    self.assertEqual(records[0]["sha256"], "TOKEN_VAZIO")
                    self.assertNotEqual(records[0]["error"], "")
                    self.assertFalse(records[0]["claim_allowed"])

    def test_successful_empty_body_is_a_valid_digest(self):
        # A completed HTTP 200 empty response has a well-defined SHA-256.
        source = COLLECT.read_text(encoding="utf-8")
        self.assertIn('[[ $rc -eq 0 && "$http_status" == 200 && -f "$body" ]]', source)
        self.assertNotIn('[[ -s "$body" ]] && sha=', source)


if __name__ == "__main__":
    unittest.main()
