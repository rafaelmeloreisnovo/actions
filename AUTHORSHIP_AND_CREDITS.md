# RAFAELIA — Authorship, attribution and source locations

**Scope:** `rafaelmeloreisnovo/actions` is a GitHub fork of `gradle/actions`. This file catalogs an independently added lane. It does not claim authorship of the entire fork, remove inherited rights or grant a new license.

## Credit register (where to find each component)

| Region | Origin classification | Responsible source and credit | Evidence/rights state |
|---|---|---|---|
| `setup-gradle/`, `dependency-submission/`, `wrapper-validation/` | Inherited candidate | Gradle Inc. and upstream contributors; `LICENSE` and upstream per-file notices | Fork's MIT notice retained; full lineage pending |
| `sources/`, `docs/`, `dist/` | Inherited/bundled candidate | Upstream contributors and relevant vendors/dependencies | Inspect embedded licenses/NOTICE and exact copied revision |
| `.github/` | Mixed | Upstream workflows **and** new local workflows | Split by exact file/commit; no aggregate authorship claim |
| `freestanding/kernel4/` | Local contribution | RAFAELIA local implementation; see `START_HERE_RAFAELIA.md` | Independently added delta; license-holder attestation pending |
| `freestanding/omega_os/` | Local contribution | RAFAELIA local implementation, separate state prototype | Local grant and independent review pending |
| `freestanding/apk_bridge/` | Local contribution | RAFAELIA local implementation, synthetic ZIP32/VM bridge | Local grant and independent review pending |
| `rafcode/l0/`, `composition/` | Local contribution candidate | Local repository commits and test contracts | Per-file lineage and rights pending |
| `freestanding/provenance_core/` | New independent implementation | Prepared at the user's direction for RAFAELIA, 2026-10-24 | Source tests are scoped; human attestation/release rights pending |
| `provenance/lineage.v1.json` | New index | Pointer-based origin map; never an authorship certificate | Requires file-level evidence |

**Attribution:** the inherited `LICENSE` contains the original MIT license and Gradle Inc. copyright. Preserve required notices with any redistribution. Never substitute merely changing a comma, variable, condition or layout for independent authorship.

**Upstream-version warning:** current `gradle/actions` licensing material identifies a proprietary vendor component, `gradle-actions-caching`. This **does not establish** that the older fork contains that component. Exact upstream base and all bundled license obligations must be compared before redistribution; `TOKEN_VAZIO` until verified.

## File-level review protocol

For any file: identify `fork HEAD → historical source/ref/path → exact blob → author/titular evidence → applicable license/attribution → dependency bundle → local delta → test receipt → human decision`. Place credits where a human can find them: file header for **new authored files**, this register for mixed/original boundaries, and `README.md` for first-level navigation. Do not mass-add invented copyright comments to inherited source or erase existing headers.

File-level origin classification is distinct from legal determination of copyright originality. APIs, number bases and common control syntax are not automatically protected expressions, but structural creative copying can create derivative-work issues.

## No regression or promotion

Protected `main` state is not inferred from workflow YAML. No inherited runtime implementation, root license, dependency, distro bundle or external branch protection is modified in this draft. A separate PR and exact-head host CI are required; no merge, release, physical execution, or independent legal review is claimed. Rollback: close the PR or revert its exact commit, preserving historical blobs.

See `provenance/lineage.v1.json` for the concise machine-readable map and `freestanding/provenance_core/README.md` for the pure source contract.

R3 = <F_ok: boundaries and credits routed, F_gap: versioned upstream provenance, human rights attestation and CI, F_next: lineaged file census before any product replacement>.

## 2026-10-31 — provider × upstream × local delta (scoped snapshot V2)

**GitHub Actions is the external CI service, not an independently authored module in this fork.** `gradle/actions` is upstream implementation; RAFAELIA paths are candidate local deltas with per-file evidence and unresolved rights. See [the explicit three-authority boundary](provenance/BOUNDARY_GITHUB_GRADLE_RAFAELIA_V2.md) and [immutable observed-blob census](provenance/attribution_snapshot.v2.json). The [stdlib-only verifier](provenance/verify_attribution.py) is a *byte-identity and consistency gate*, not a legal author certificate or a claim of remote CI PASS. On 2026-10-31 the merged Atlas APK source is present but an exact-head run receipt was not returned by the scoped query. `claim_allowed=false` for release/whole-fork attribution. Reuse of the same `atlas.c` blob in L0 and Android is recorded as source reuse, not a second original creation.
