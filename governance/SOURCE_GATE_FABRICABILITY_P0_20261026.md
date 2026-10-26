# RAFAELIA / Actions — P0 source-gate fabricability closure candidate (2026-10-26)

**STATUS:** LOCAL_PASS_SCOPED / SOURCE_IMPLEMENTED_IN_HOLD_BRANCH / PROVIDER_ENFORCEMENT_OPEN / REMOTE_NOT_OBSERVED / **PROMOTION=HOLD**, `claim_allowed=false`.

## 1 — Objective and change boundary

The repository is a fork of Gradle Actions. Inherited Gradle/Node/Java code, licensing and distribution are not modified or claimed as independently authored. A previously tested RAFAELIA source validator did not include ordinary untracked files, and its 2026-10-24 HOLD patch still accepted Git-ignored source files under production-critical roots. A new limited successor is tested against `main@2df8a3773243f4f995784c8de0cbadb6902b23c2`. This new branch inherits current `main` (not the diverged old HOLD branch), preserves the old branch, adds one small CI gate and one explanatory README append. No merge or release.

## 2 — Source-to-test trace

| Requirement / risk | Source implementation | Test/falsifier | Local state |
|---|---|---|---|
| Exact HEAD and no changed tracked content | `rafcode/verify-source/verify.sh` | original dirty/index/wrong-SHA negatives | PASS_SCOPED |
| No ordinary untracked inputs | `ls-files --others --exclude-standard` | rogue C/H and newline-path negative | PASS_SCOPED |
| No **ignored** input in core, receipt, policy or workflow roots | `ls-files --others --ignored --exclude-standard` restricted to five roots | `rogue.inc` (Dispatch), `policy.json` (governance), `rogue.yml` (Actions) | PASS_SCOPED |
| Avoid rejecting unrelated ignored build caches | critical-root restriction | `build/cache.inc` still accepted | PASS_SCOPED |
| Bind gate testing to source HEAD on CI | `.github/workflows/ci-rafcode-source-gate.yml`: SHA fetch, before + after source gate, 14 negative/positive tests | YAML parse and self-contained trigger/security check | LOCAL_STATIC_PASS; REMOTE_NOT_OBSERVED |
| Preserve Dispatch L0 behavior | no edits to its C / header / tests | previously archived 3-target `verify.sh`, same object SHA-256 | LOCAL_PASS_SCOPED |

Source shell candidate exact Git blob: `99431a9b6dd0d3166ec5ccf68773106c37182413`, SHA-256 `9001ff0a02443bb78a1c119366aadbacbbedaef4091b98617d31ba72d7a6dcc5`.
Test candidate exact blob: `b1639f367e589966a2292eb050c50952998b7df5`, SHA-256 `5dcfea4bd1875b84c588f83f6a2d8c32dc5792f53ccc7151c03f364dcd83d54c`.
Workflow blob: `e3e4418957184434877aa3d3770d0bb3a3c9c8cc`, SHA-256 `d5a0e7f1e0c5a0be690df52d468e0ccd75278ff2693fef1bddb6339d2d174a43`.
Local `python3 .../test_verify.py -v` = **14/14 PASS**. Standalone `dispatch_l0/tests/verify.sh`: x86-64, ARMv7, AArch64 objects with no undefined symbols and double-build byte equality, hosted sanitized harness at -O0/-O2 **PASS_SCOPED**, not physical execution. Source and tests were byte-identical by Git blob to locally tested files before commit.

## 3 — Residual failure-mode inventory (never auto-promote)

| Priority | Type | Uncertainty and potential failure | Required evidence/gate |
|---|---|---|---|
| P0 | PROVIDER_AUTHORITY | `main.protected=false`, zero repository rulesets; changes may merge without independent review | GitHub readback required checks/reviews + **negative rejected merge test**, not workflow YAML alone |
| P0 | EXECUTION_NOT_OBSERVED | No recent exact-HEAD checks/runs returned; scheduling/billing/permissions root cause unresolved | Actions run ID / HEAD / jobs / steps / logs and observed conclusion |
| P1 | INPUT_SCOPE_GAP | Ignored or generated inputs **outside** protected roots can influence later builds | per-producer hermetic input allowlist + asset SHA binding |
| P1 | TOCTOU_GAP | Source files can mutate after the gate and before compilation | pre/post gate + exact source and binary hashes; trusted build isolation |
| P1 | TOOLCHAIN_TRUST | Git SHA and compilation are not proof of compiler provenance or supply-chain integrity | signed/reproducible toolchain receipt, SBOM and review |
| P1 | RECEIPT_BINDING | Artifact digest emitted after falsifier could differ from artifact actually tested | independent negative mutation test and before/after artifact digest agreement |
| P1 | RIGHTS_PRIVACY | Third-party fork licensing/attribution unresolved per delta and possible sensitive host content | holder/license mapping, minimal logs, no personal/child data published |
| P1 | HARDWARE_ATTESTATION | CPU, watchdog, GPU, NUMA and ART remain caller declarations or separate interfaces | actual device/ISA/ABI, trusted driver, fault injection, artifact SHA |
| P2 | PERFORMANCE | Extra Git enumeration cost not benchmarked under full monorepo tree | paired latency baseline and resource limits before promoting |
| P2 | SECURITY_CLAIM | ISO/NIST mention is not certified conformity; fail-closed check is not Zero Trust architecture alone | scoped requirement/control/evidence mapping and independent assessment |

**Observations:** No secrets, user records, personal data or copyrighted external implementations were introduced in new source. Inherited upstream MIT and original attribution remain unchanged. Git blob SHA-1 is an object identifier, not signed provenance; SHA-256 receipt is not a signature. `TOKEN_VAZIO != 0`. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. No certification, full compliance, hardware execution, physical double watchdog, automatic fallback or rollback claimed.

## 4 — Acceptance, rollback, and R3

- **F_ok:** explicit restricted ignored-input falsifier and compatibility positive, 14/14 local host tests; Dispatch L0 regression unchanged; exact candidate file hash identity; workflow static integrity.
- **F_gap:** GitHub server-side protection, real CI execution and provider root cause, independent rights review, performance, ignored inputs outside critical scope, artifact/TOCTOU binding.
- **F_next:** have administrator establish required reviews/checks on protected main and observe test PR rejection, run exact HEAD CI and inspect job steps/logs, review rights, only then consider a reviewed PR for this hotfix.
- **Rollback:** do not adopt this isolated HOLD branch, or a separately authorized targeted revert of its eventual commit; preserve original branch history, never delete/mutate `main` by this proposal.

**No promotion or merge authorization is created by this branch or document.**
