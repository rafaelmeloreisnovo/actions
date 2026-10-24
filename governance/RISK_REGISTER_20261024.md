# RAFAELIA Ω — Engineering risk ledger / 2026-10-24 (candidato, sem promoção)

Escopo: repositório `rafaelmeloreisnovo/actions`. Observed baseline `main@39dfc83aec20c2daff532e7f45e6f9f76cc323d5`; this text indexes a bounded assessment, **not** an audit of every byte or a claim of conformity.

## Boundaries and route
`L0 (kernel4 / omega_os / apk_bridge / rafcode / rights_core)` → `L1 host compilers & test harness` → `L2 provider workflow / physical Android consumer` → `L3 independent rights, governance and release gate`.

The inherited `gradle/actions` implementation and its `dist/` remain third-party; DO NOT mark as separately authored or freestanding. No branch deletes or autonomous merges. Whole-fork authorial claim=false. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

## Measured issues, accepted risk, and falsifiers

| ID / priority | Observed risk | Controlled improvement / falsifier | Closure gate |
|---|---|---|---|
| R-001 P0 | RAFCODE workflow fetched `GITHUB_REF`, which can select PR merge-ref instead of source HEAD | Fetch immutable `github.event.pull_request.head.sha`; require `git rev-parse HEAD` equality | GitHub Actions job at exact PR HEAD; negative wrong-SHA attempt |
| R-002 P0 | Ω-OS Python `ctypes.Slot` omitted C field `epoch`; 12 vs 16 byte slot (116 vs 148 byte context) | Mirror four `ou32` fields; ABI size/offset assertion | Dedicated Ω-OS hosted state/replay tests and sanitizer at same HEAD |
| R-003 P1 | Provenance-core caller may alias request and receipt buffers | Snapshot two input words before any output writes, bounded no-libc C | Exhaustive 2×128 masks, invalid bits, overlap fixture, x86/ARM object gate |
| R-004 P0 | `main` observed unprotected; no provider enforcement inferred from YAML | Human/admin provider ruleset and independent review assessment | Provider readback + required checks + explicit authority, not file change |
| R-005 P0 | PR #9 merged and source branch deleted on 2026-10-24 by account activity | Successors append-only; retain branch refs and commit hashes | No branch deletion in this draft; rollback by selective revert or close PR |
| R-006 P1 | Evidence Registry uses write token, scheduled external URLs, unpinned upstream actions | Separate source-scoped threat audit, pinned refs, redirect/SSRF controls, read-only collection | Falsifier with hostile endpoints; no external fetch credentials or unrestricted egress |
| R-007 P1 | ZIP32 structural probe lacks signature, decompression, CRC and alias/overlap validation | Preserve narrow `STRUCTURAL_ZIP32_SUBSET` label; bounded hostile ZIP corpus | Anti-alias/duplicate local-header tests + real `apksigner` separate boundary |
| R-008 P1 | Inherited `dist/` and upstream version legal chain incompletely resolved; new upstream licensing differs | Reconcile exact fork point and distribution dependencies with notices and source hashes | Human file-level provenance/rights review |
| R-009 P2 | L0 object compilation not the same as executable freestanding ELF | Linker entry/ELF/relocation/stack tests separately per architecture | Same exact artifact host receipt; never infer physical boot |
| R-010 P2 | Ω-OS actor identity supplied by untrusted caller | Authenticated principal adapter + bounded capabilities + replay guard | Model/fault-injection/physical authorization test |
| R-011 P2 | No exact ARM32/ARM64 device execution for this change | Reproducible physical devices with controlled consent | Signed artifact SHA binding and hardware receipt |
| R-012 P3 | Numerical reductions and symbol-level heuristics may optimize away observability | Differential compiler tests, disassembly census and traceable performance baseline | Performance delta + functional invariants; revert on ABI/race/portability regression |

## 6Σ DMAIC — measurable closure not a certification
Define: source authority, invariants and CTQ. Measure: state and exact SHA, build, tests, rights and provider status. Analyze: priority, uncertainty and attack surfaces. Improve: surgical source/test changes without modifying upstream. Control: exact-head CI, independent reviewer, rollback commits, append-only μWRITE and human merge authority.

Mapping is **informative**, not an ISO/NIST certification: NIST SP 800-218 PO/PS/PW/RV (secure development, provenance, vulnerabilities); ISO/IEC 27001:2022 risk-controlled ISMS; ISO 9001 continual improvement; ISO 8000 data-quality concepts of provenance/accuracy/completeness. A framework mention is not an assessed conformity claim. Risk cannot be mathematically zero without threat assumptions; `TOKEN_VAZIO` expresses missing evidence.

## Proposed next experiment
First close R-001/R-002 by source-bound CI; then audit R-006/R-007 as separate work without changing upstream runtime. A hosted sanitizer PASS does not authorize release/merge, hardware boot or legal claims.

R3 = <F_ok: 3 local bugs and checks typed, F_gap: hosted Actions/provider/reviewer/hardware evidence unresolved, F_next: exact-HEAD CI and least-privilege review>.

### Versioned standards refresh — 2026-10-24 (informative)

The current edition is ISO 9001:2026 (ISO published 16 September 2026), replacing ISO 9001:2015; see https://www.iso.org/quality-management/iso-9001-2026 . Use it as guidance for documented risks, opportunities and continuous improvement, not as a certification. NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final and ISO/IEC 27001:2022: https://www.iso.org/standard/27001 . ISO 8000 is a multi-part data-quality family; exact part/applicability remains TOKEN_VAZIO rather than presuming a single applicable normative clause. DMAIC and PDCA are complementary improvement cycles, not a proof of a statistical Six Sigma level.

**New discovered regression closure**: R-003-A: rights-core output null guard must precede any input dereference, including an intentionally invalid input pointer. Local host test with a non-dereferenceable input and null result PASS on candidate source. Explicitly keep `claim_allowed=false` and re-run exact-head provider tests after this commit.

### Supersessão declaratória N-001 — distinção de certificação (2026-10-24)

Este inventário documenta **boas práticas inspiradas nas referências técnicas**, não comprova que a RAFAELIA possui certificação ou atende integralmente a alguma norma. Sem documento de certificação autêntico, escopo, titular, emissor e vigência verificados, a alegação de certificação permanece **BLOCKED** (`TOKEN_VAZIO_NOT_OBSERVED` para a prova); nenhuma afirmação de conformidade plena é autorizada. Correção de comunicação e governança, não revoga fatos anteriores nem altera os núcleos C. Fonte de política: [NORMATIVE_CLAIM_POLICY_V1.md](NORMATIVE_CLAIM_POLICY_V1.md). `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.
