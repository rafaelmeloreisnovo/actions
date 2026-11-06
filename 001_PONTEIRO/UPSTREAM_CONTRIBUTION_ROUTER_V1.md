# 001_PONTEIRO · Upstream Gradle Actions contribution router V1

**Authority:** upstream source `gradle/actions@c8a326d85724fce2ae59a38810306f4a058f26a4`; private RAFAELIA evidence/ledger only in Drive/Supabase; public contributions only in `rafaelmeloreisnovo/actions`.
**Observed:** 2026-11-06; static Git diff and issue status. This is **not** an upstream PR nor a CI PASS.

## Routes: minimal readable entrypoint
- Machine issue register and semantic edges: [roadmap.v1.json](../provenance/upstream_issues_roadmap.v1.json)
- Fail-closed local metadata gate: [verify_upstream_issues_v1.py](../provenance/verify_upstream_issues_v1.py)
- Negative tests: [test_upstream_issues_v1.py](../provenance/tests/test_upstream_issues_v1.py)
- Source contribution rules: [CONTRIBUTING.md](https://github.com/gradle/actions/blob/c8a326d85724fce2ae59a38810306f4a058f26a4/CONTRIBUTING.md) and [CLAUDE.md](https://github.com/gradle/actions/blob/c8a326d85724fce2ae59a38810306f4a058f26a4/CLAUDE.md).
- Related legal boundary (separate PR): [#26](https://github.com/rafaelmeloreisnovo/actions/pull/26), **not** an upstream code patch.

## CURRENT_STATE — only bounded checks
| Priority | Upstream issue | Candidate | State | Checkpoint (proposed, NOT a maintainer deadline) |
|---|---|---|---|---|
| P0 | [#549](https://github.com/gradle/actions/issues/549): persistent debug Gradle properties | [Draft #27](https://github.com/rafaelmeloreisnovo/actions/pull/27), `c9ed8091b19f14e796bfad23bfb103d51f4a32bc` | IMPLEMENTED_UNTESTED | 2026-11-09: GitHub exact-HEAD CI / unit |
| P1 | [#656](https://github.com/gradle/actions/issues/656): HTTP 503 graph submission | [Draft #28](https://github.com/rafaelmeloreisnovo/actions/pull/28), `4bb062b415c6217013e75f82d5a4067816265ddf` | IMPLEMENTED_UNTESTED | 2026-11-09: CI/negative tests |
| P1 | [#316](https://github.com/gradle/actions/issues/316), [#722](https://github.com/gradle/actions/issues/722): reusable/cache collisions | None | BLOCKED_PRODUCER: v6 enhanced cache owned by separate `gradle/actions-caching`; basic provider comparison required | 2026-11-13: authority and reproduction |
| P1 | [#813](https://github.com/gradle/actions/issues/813), [#286](https://github.com/gradle/actions/issues/286): wrapper signature and distribution verification | None | DESIGN_PENDING: key trust/canonical mirrors and offline behavior | 2026-11-16: contract and negative cases |
| P1 | [#1088](https://github.com/gradle/actions/issues/1088): Gradle 9.8 dependency graph build failure | None | NEEDS_REPRO, producing code owner TOKEN_VAZIO | 2026-11-13: minimal reproduction |

No binding upstream deadlines or staff assignments were observed; all dates are internal **proposed checkpoints**, not promises or observed external SLAs.

DCO evidence: [upstream .github/dco.yml](https://github.com/gradle/actions/blob/c8a326d85724fce2ae59a38810306f4a058f26a4/.github/dco.yml) disables DCO checking for Gradle organization members. No verified contributor sign-off is present on these candidate commits: `DCO_ATTESTATION=TOKEN_VAZIO`. A reviewer must check applicability and the rightsholder must authorize the exact statement; never fabricate `Signed-off-by` text.

## Pipeline/checkpoints
`INTAKE → SOURCE_AUTHORITY → REPRO → NARROW_PATCH → ADVERSARIAL_TEST → CI → MAINTAINER_REVIEW → UPSTREAM_MERGE → RECEIPT`.

1. Validate immutable base and changed-file allowlist; never place RAFAELIA-specific documents in an upstream code PR.
2. Run `./build`, `./build all` and the appropriate Gradle upstream integration workflow **in a suitable Node 24 environment**, ensuring provider run_id + exact head + exit state + logs.
3. For #549: original/created/modified/symlinked/missing property file; for #656: success, transient 503, 502 exhaustion, 403/422 and unknown-error no-retry; retain existing documented semantics.
4. Reject promotion on missing provider CI, ambiguous vendor provenance, hidden data, unexpected file diff or failed negative tests.
5. Submit upstream PR only after the focused gate and maintainers' contribution instructions permit it. Public GitHub branch ≠ submission to upstream.
6. Preserve a receipt in private Drive/Supabase; update this pointer only if state materially changes. Corrections use append-only successor.

**Producer split**: upstream `gradle/actions` main v6 includes proprietary enhanced caching supplied by `gradle/actions-caching`. Never hand-edit `sources/vendor/gradle-actions-caching` or `dist/`. Dist is CI-generated. Do not assume missing upstream code is ours or MIT.

Academic methodological context, not evidence that our changes pass: [CI-Repair-Bench](https://www.alphaxiv.org/abs/2604.27148), which evaluates repairs through native full CI execution beyond isolated tests.

**R3** = ⟨F_ok: two isolated draft patches and seven-route graph; F_gap: no CI returned, upstream review, producer unknown for #1088; F_next: exact-head CI on PRs #27/#28 then surgical revision or rollback⟩
