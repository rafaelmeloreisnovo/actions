"""Fail-closed provider receipt verifier mocks; no live network or secrets."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

here=Path(__file__).parent
spec=importlib.util.spec_from_file_location("verifier",here/"provider_verify.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
repo="rafaelmeloreisnovo/BOOTSTRAPsys"; sha="a"*40
artifact=b"fixture\n"; script=b"exit 0\n"
def h(b): return hashlib.sha256(b).hexdigest()
def blob(raw):
    return {"type":"file","encoding":"base64","size":len(raw),
            "content":base64.b64encode(raw).decode("ascii"),
            "sha":hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()}
def rec():
    r={"schema":v.SCHEMA,"repository":repo,"source_commit_sha":sha,
       "run_id":40258763936,"run_attempt":1,
       "run_url":"https://github.com/"+repo+"/actions/runs/40258763936",
       "artifact_path":"README.md","artifact_size":len(artifact),
       "artifact_sha256":h(artifact),"falsifier_id":"SOURCE_DIGEST_NEGATIVE",
       "falsifier_path":".github/rafcode/falsifier_source_integrity.sh",
       "falsifier_script_sha256":h(script),"falsifier_exit_code":0,
       "falsifier_state":"PASS_SCOPED","github_run_conclusion":"NOT_YET_ATTESTED",
       "independent_review":"NOT_RUN","receipt_type":"PROVISIONAL_HOST_TEST",
       "claim_allowed":False,"promotion":"HOLD"}
    seal(r);return r
def seal(r):
    r["receipt_sha256"]=h(json.dumps({k:v for k,v in r.items()
        if k!="receipt_sha256"},ensure_ascii=True,sort_keys=True,
        separators=(",",":")).encode("ascii"))
def provider(path):
    if "/jobs?" in path:
        return {"jobs":[{"id":900,"conclusion":"success","steps":[
            {"name":"Author-owned action — run, artifact, falsifier SHA256 receipt",
             "status":"completed","conclusion":"success"}]}]}
    if "/actions/runs/" in path:
        return {"id":40258763936,"run_attempt":1,"head_sha":sha,
                "status":"completed","conclusion":"success"}
    if "/contents/README.md" in path:return blob(artifact)
    if "/contents/.github/" in path:return blob(script)
    raise AssertionError(path)

class ProviderReceipts(unittest.TestCase):
    def test_success_only_scope(self):
        r=v.verify(rec(),provider)
        self.assertEqual(r["provider_execution"],"SUCCESS_VERIFIED_SCOPED")
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["domain_runtime"],"NOT_PROVEN")
    def test_digest_tamper(self):
        r=rec();r["artifact_sha256"]="0"*64
        with self.assertRaisesRegex(v.VerifyError,"RECEIPT_DIGEST"):
            v.verify(r,provider)
    def test_false_promotion(self):
        r=rec();r["claim_allowed"]=True;seal(r)
        with self.assertRaisesRegex(v.VerifyError,"FALSE_PROMOTION"):
            v.verify(r,provider)
    def test_wrong_provider_commit(self):
        def wrong(path):
            x=provider(path)
            if "/actions/runs/" in path and "/jobs" not in path:x["head_sha"]="b"*40
            return x
        with self.assertRaisesRegex(v.VerifyError,"PROVIDER_RUN"):
            v.verify(rec(),wrong)
    def test_incomplete_run(self):
        def incomplete(path):
            x=provider(path)
            if "/actions/runs/" in path and "/jobs" not in path:x["status"]="in_progress"
            return x
        with self.assertRaisesRegex(v.VerifyError,"PROVIDER_RUN"):
            v.verify(rec(),incomplete)
    def test_action_step_not_observed(self):
        def absent(path):
            x=provider(path)
            if "/jobs?" in path:x["jobs"][0]["steps"]=[]
            return x
        with self.assertRaisesRegex(v.VerifyError,"ACTION_STEP"):
            v.verify(rec(),absent)
    def test_artifact_drift(self):
        def drift(path):
            x=provider(path)
            if "/contents/README.md" in path:x=blob(b"drift")
            return x
        with self.assertRaisesRegex(v.VerifyError,"ARTIFACT_BYTES"):
            v.verify(rec(),drift)
    def test_script_drift(self):
        def drift(path):
            x=provider(path)
            if "/contents/.github/" in path:x=blob(b"exit 1\n")
            return x
        with self.assertRaisesRegex(v.VerifyError,"FALSIFIER_BYTES"):
            v.verify(rec(),drift)

if __name__=="__main__":
    unittest.main()
