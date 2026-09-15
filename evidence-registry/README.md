# Evidence Registry — AI Releases & Public Claims

Evidence-first collector for public release pages, changelogs, documentation and other public claims.

## Invariants

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM

- Preserve source URL and retrieval timestamp.
- Store SHA-256 of retrieved body.
- Preserve HTTP metadata when available.
- Never infer a historical publication date from retrieval time.
- Contradictions are recorded, not silently resolved.
- Missing fields remain TOKEN_VAZIO.
- Collection does not itself establish wrongdoing or any legal conclusion.

## Output

Each run creates an append-only JSONL evidence ledger plus raw response bodies and a SHA256SUMS manifest.

## Usage

```bash
python3 evidence-registry/collector.py --sources evidence-registry/sources.txt --out evidence
```

The source list is intentionally small at bootstrap. Expand only with public, relevant, attributable sources.
