# Provenance boundary V2 — Gradle upstream × GitHub Actions service × RAFAELIA

**Repository:** `rafaelmeloreisnovo/actions` (fork of `gradle/actions`)  
**Frozen observation:** `main@e536d230cd34b66fafffa073d26b39b2989e6da9` (2026-10-31)  
**Scope:** selected file-level census, not exhaustive copyright clearance, not release authorization.

## Three authorities, never interchangeable

| Layer | Real authority | What the fork may truthfully claim |
|---|---|---|
| GitHub Actions hosted service, hosted runners, event engine, hosted checks | GitHub | A workflow invokes this platform; it is **not** a locally authored CI engine |
| Gradle Actions (setup-gradle, dependency-submission, wrapper-validation, bundles and docs) | `gradle/actions` and individual upstream contributors/vendors | Inherited or bundled content retains applicable upstream rights and attribution |
| RAFAELIA fork-local additions | Local contributors, subject to proof and rights review | Specific commits, paths, independent additions, adaptations and tests; **not** whole-fork authorship |

A workflow YAML is a repository file, while the service running it is external. An external `uses: actions/checkout@...` component does not become local source merely because a local workflow calls it. A successful provider run proves only the bounded checks executed in that run, for that commit and environment; it is not a copyright decision, an Android-device test, or physical ARM execution.

## Evidence frozen today

`attribution_snapshot.v2.json` binds nine concrete paths to Git **blob SHA-1** values, and `verify_attribution.py` recomputes the Git blob format from working-tree bytes, rejecting changed, missing, symlinked, duplicated, traversed or incorrectly typed paths. SHA-1 is used here only because Git identifies blobs this way; it is not a collision-resistant legal certificate or a provenance chain by itself.

One important anti-duplication fact: `freestanding/atlas_drive_l0/atlas.c` and `android/atlas_wizard/native/atlas.c` have the **same observed blob**. The latter is a reused local source, not a second independently authored implementation.

PR #22 merged into `main`, but the observed GitHub Actions query returned **zero workflow runs** for the merge head and the PR's source head. This is a scoped observation, not proof that no workflow was ever executed. `CI_PASS=false` in this snapshot; the independent provider receipt remains `TOKEN_VAZIO`.

## Falsifiers and authority gates

Run from the repository root:

```sh
python3 provenance/verify_attribution.py
python3 -m unittest discover -s provenance/tests -p 'test_*.py' -v
```

The first command is an exact-blob census gate, not a GitHub provider attestator. The unit tests exercise tampered blobs, invented rights, false CI PASS, provider misattribution, traversal, symlinks, duplication and source reuse. The existing `ci-rafaelia-rights.yml` can run these tests at exact PR HEAD without creating another workflow.

**Release gate remains blocked** until file-level upstream fork-point comparison, license/NOTICE/component audit of `dist/`, human holder attestation for local deltas, independent review and exact provider run receipts. In particular, neither GitHub ownership, a verified merge signature nor SHA equality establishes exclusive authorship.

**Rollback:** close the draft PR or selectively revert its commits. This snapshot does not replace `provenance/lineage.v1.json`, inherited code or the fork's MIT notice; it supersedes stale presentation only as a later, scoped observation.

R3 = <F_ok: three authorities and nine observed blob identities separated, F_gap: upstream rights/complete census/provider CI/physical device, F_next: falsify at exact PR head, then review per-file attribution before merge>.
