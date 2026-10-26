# RAFAELIA P0 — fechamento de gate documental (2026-10-26)

Source: main `47e0ad95703009bfaaa902f605fd3bf69aae4b48`. This is an **append-only proposal**; no automatic merge, branch deletion, provider-settings mutation, or inherited Gradle source change.

## Fixed
- `governance/verify_normative_claims.py` is a pure standard-library HOST validation gate: unknown evidence is **typed unknown**, never false/zero/PASS; no certification/conformity claims may be promoted from repo flags.
- Strict JSON parser rejects duplicate object keys before policy inspection; unknown/missing fields, weak authority, altered evidence requirements and invalid booleans are rejected.
- `governance/tests/test_verify_normative_claims.py` adds 14 negative/mutation-oriented tests, while retaining the original tests.
- Normative CI is triggered for every PR rather than only a small paths filter, with immutable commit checkout and no credential persistence. This workflow cannot enforce branch protection by itself.

## Evidence
Local HOST Python 3 execution on tested source: **14/14 PASS**, `DOCUMENT_ONLY_ACCEPTED; CERTIFICATION=NOT_VERIFIED; FULL_CONFORMITY=NOT_CLAIMED`. Exact local SHA-256 receipts for the candidate sources must be matched against GitHub Git blobs after commit. GitHub-hosted exact HEAD checks remain **NOT_OBSERVED**, not inferred from local PASS.

## Provider P0 still blocked
GitHub metadata on 2026-10-26: `delete_branch_on_merge=true`, `main.protected=false`, `has_issues=false`. Neither administrator settings nor required checks can be changed with the current connector actions. Owner must disable branch auto-deletion and configure protected `main` with required independent review and exact-head checks. No new merge authorized by automation.

## Limits
A manifest checker cannot search arbitrary project text for improper normative claims, validate a legal certificate, apply full text of ISO/IEC requirements, or establish certification. These remain human/external evidence gates. The project may accurately describe **boas práticas inspiradas nas normas**, only for observed control scope.

R3: F_ok = local negative gate tested, GitHub source branch and receipt; F_gap = provider CI/branch controls/certification proofs; F_next = independent review and exact HEAD Actions receipt. Claim_allowed=false.
