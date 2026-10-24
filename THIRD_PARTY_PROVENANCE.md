# Third-Party Provenance — Gradle Actions fork

Status: THIRD_PARTY_UPSTREAM_WITH_LOCAL_DELTAS / claim_allowed=false for whole-repository authorship.

## Upstream authority
- Source: `gradle/actions`
- Destination: `rafaelmeloreisnovo/actions`
- Relationship: GitHub fork.
- Destination repository license detector currently reports MIT; upstream legal files and notices remain authoritative for inherited content.

## Authorship boundary
Inherited Gradle Actions code, workflows, JavaScript/TypeScript bundles, documentation and history remain third-party. Fork ownership or local workflow changes do not transfer copyright in inherited material.

RAFAELIA authorship is limited to independently added deltas supported by path/commit/blob evidence. Unknown lineage is `TOKEN_VAZIO`; whole-repository authorship claim is not allowed.

## Distribution control
Preserve applicable license/copyright notices and audit generated/bundled action distributions because vendored `dist` output can contain third-party dependencies with separate notices.

Required record: `source/ref/path -> destination -> local delta -> dependency/bundle -> holder -> license -> obligations -> evidence -> release gate`.


## 2026-10-24 versioned audit note (draft delta)

The upstream `gradle/actions` currently includes licensing text identifying a separately licensed vendor component, `gradle-actions-caching`. This is **not** evidence that the checked-out fork contains that exact component. Versioned source and bundled `dist/` obligations require a file-by-file comparison; do not overwrite the fork's existing MIT notice or assert all content is MIT. Use `AUTHORSHIP_AND_CREDITS.md` and `provenance/lineage.v1.json` for index/credits. The new freestanding rights-core is an isolated local delta; a structural PASS is not a legal originality certificate.
