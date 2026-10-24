"""Offline zero-network policy falsifiers for RAFAELIA evidence registry."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HOST_FILE = ROOT / "evidence-registry" / "allowed_hosts.v1.txt"
SOURCES = ROOT / "evidence-registry" / "sources.tsv"
COLLECT = ROOT / "evidence-registry" / "collect.sh"

class SourcePolicy(unittest.TestCase):
    def test_every_existing_source_matches_explicit_allowlist(self):
        allowed = {x.strip() for x in HOST_FILE.read_text().splitlines()
                   if x.strip() and not x.startswith("#")}
        self.assertTrue(allowed)
        for line in SOURCES.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            provider, klass, url = line.split("\t")
            parts = urlsplit(url)
            with self.subTest(url=url):
                self.assertTrue(provider and klass)
                self.assertEqual(parts.scheme, "https")
                self.assertIn(parts.hostname, allowed)
                self.assertIsNone(parts.username)
                self.assertIsNone(parts.password)
                self.assertIsNone(parts.port)

    def test_collector_never_contacts_denied_hosts(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            fake = tmp / "curl"
            fake.write_text("#!/bin/sh\nprintf 'CONTACTED' >> \"$MOCK_LOG\"\nexit 44\n")
            fake.chmod(0o755)
            inputs = tmp / "inputs.tsv"
            inputs.write_text(
                "Denied\tprivate\thttp://127.0.0.1/latest/meta-data\n"
                "Denied\tuserinfo\thttps://github.com@127.0.0.1/private\n"
                "Denied\tunlisted\thttps://evil.example.invalid/test\n")
            env = dict(os.environ, RA_HOSTS_FILE=str(HOST_FILE),
                       PATH=str(tmp) + os.pathsep + os.environ["PATH"],
                       MOCK_LOG=str(tmp / "mock.log"))
            out = tmp / "archive"
            subprocess.run(["bash", str(COLLECT), str(inputs), str(out)],
                           cwd=ROOT, env=env, capture_output=True, text=True, check=True)
            self.assertFalse((tmp / "mock.log").exists())
            records = [json.loads(s) for s in (out / "latest-ledger.jsonl").read_text().splitlines()]
            self.assertEqual(len(records), 3)
            self.assertTrue(all(r["error"] == "DENIED_URL_BY_HOST_OR_SCHEME_POLICY" for r in records))
            self.assertTrue(all(r["sha256"] == "TOKEN_VAZIO" and not r["claim_allowed"] for r in records))

    def test_curl_arguments_prohibit_redirects_and_non_https(self):
        script = COLLECT.read_text()
        self.assertIn("--proto '=https'", script)
        self.assertIn("--proto-redir '=https'", script)
        self.assertIn("--max-filesize 10485760", script)
        self.assertNotIn("curl -L ", script)
        self.assertNotIn("curl --location", script)

if __name__ == "__main__":
    unittest.main()
