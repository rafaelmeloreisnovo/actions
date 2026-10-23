# RAFAELIA Ω — Composition router / next steps (2026-10-23)

**Repository:** `rafaelmeloreisnovo/actions` (fork of `gradle/actions`). **Scope:** local RAFAELIA work only. Do not alter or relicense upstream Gradle Actions.

**Baseline observed:** `143477ff8636a65a920361646665fe08af23b6a2` on `main`.
`main` was observed unprotected / enforcement OFF; an exact-HEAD Actions-run query returned no runs. Both are **observations**, not claims that workflows never ran. This document and its local validation are **not an execution receipt**.

## The five routes

| Route | Producer input | Verified by existing source gate | Missing bridge |
|---|---|---|---|
| GOV | `START_HERE_RAFAELIA.md`, `THIRD_PARTY_PROVENANCE.md` | documentary provenance | branch controls, human review, local license authority |
| K4 | `freestanding/kernel4/` | linked ELF class, entry, zero-undefined, size, reproducibility on hosted CI | exact-current CI, physical ARM32/64 runtime |
| RAFCODE | `rafcode/l0/` | local object symbol/dependency gate | exact PR-head checkout receipt |
| APK | `freestanding/apk_bridge/` | cross-target objects + synthetic ZIP32/VM tests | ZIP hardening; Android producer, build/sign/install |
| OMEGA | `freestanding/omega_os/` | host state falsifiers + freestanding objects | actor identity, virtual boot, isolation and real task runtime |

```
INTENT → CURRENT_STATE → SOURCE_MIN → AUTHORITY → L0 source
       → SAME-HEAD HOST CHECKS → CROSS-LANE RECEIPT (NOT AUTOMATIC)
       → L1 producer/build → L2 physical consumer → REVIEW + RIGHTS
       → PROVIDER ENFORCEMENT → ALLOWED CLAIM (only if proven)
```

**Boundaries:** K4 freestanding linked ELF != bootloader. Ω-OS logical BOOT != firmware boot or OS installation. APK ZIP32 subset != authenticated/signed/installed APK. Build tools/Java/Gradle/Android SDK are **host-side dependencies**, not L0 runtime dependencies. Do not call upstream sources locally authored.

## P0 → P3 actionable sequence

Machine-readable details, owner lanes, typed gaps, falsifiers, acceptance and rollback are in [next_steps.v1.json](next_steps.v1.json).

1. **P0:** provider protection/review authority; repair RAFCODE exact-head PR checkout; collect source-bound independent receipts from all lanes. This proposal does **not** modify provider rules.
2. **P1:** stress/fuzz ZIP32 subset without claiming signature validity; bind real Android/Termux producer with AAPT2/D8/apksigner external boundary; execute ARM physical exact-artifact tests.
3. **P2:** Ω-OS actor attestation/serialization/invariants, then QEMU virtual boot in a producer repository with its own authority, not assumed to exist.
4. **P3:** file-level rights, independent review, release gate, provider protections, and rollback receipts before any promotion.

**Control:** Run `python3 composition/validate.py` and `python3 -m unittest discover -s composition/tests -v`. The dedicated workflow checks only this static contract and source routes. It does not run every lane or prove Android hardware, CI green, OS boot, signing, or licenses. No merge is authorized by this document.

**Receipt format:** `μID | ts | source/ref | parent | kind | Δsummary | routes | evidence | gap | next | rollback | hash/ref`. Write only material deltas; successor records supersede, never erase.

**R3** = <F_ok: source routes and priority dependencies are explicit; F_gap: provider authority, exact-HEAD joint evidence, physical runtime, producer rights remain typed TOKEN_VAZIO; F_next: run scope-specific CI and resolve P0-02 without touching inherited paths>.
