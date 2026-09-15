#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, re, urllib.request
from datetime import datetime, timezone

UA = "EvidenceRegistry/1.0 (+public-source provenance collector)"

def safe_name(url):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", url)[:180]

def fetch(url, outdir):
    retrieved = datetime.now(timezone.utc).isoformat()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    record = {"source_url": url, "retrieved_at": retrieved, "source_date": None,
              "status": None, "content_type": None, "sha256": None,
              "raw_artifact": None, "error": None, "claim_allowed": False}
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            record["status"] = getattr(r, "status", None)
            record["content_type"] = r.headers.get("Content-Type")
            digest = hashlib.sha256(body).hexdigest()
            record["sha256"] = digest
            raw = outdir / "raw" / f"{safe_name(url)}__{digest[:16]}.bin"
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(body)
            record["raw_artifact"] = str(raw)
    except Exception as e:
        record["error"] = f"{type(e).__name__}: {e}"
    return record

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", default="evidence")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    urls = [x.strip() for x in pathlib.Path(args.sources).read_text().splitlines()
            if x.strip() and not x.lstrip().startswith("#")]
    ledger = out / "ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        for url in urls:
            rec = fetch(url, out)
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            print(json.dumps(rec, ensure_ascii=False))
    manifest = out / "SHA256SUMS"
    files = sorted(p for p in out.rglob("*") if p.is_file() and p != manifest)
    manifest.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n" for p in files))

if __name__ == "__main__":
    main()
