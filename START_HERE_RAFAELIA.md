# START HERE — Gradle Actions fork + RAFAELIA local delta

Status: `FORK_LOCAL_NAVIGATION`  
Observed: `2026-10-04`  
Repository: `rafaelmeloreisnovo/actions`  
Base branch: `main`

This repository is a GitHub fork of **`gradle/actions`**. The inherited Gradle Actions project remains third-party. This file only routes humans and AI agents between the inherited product and the independently added local surface.

## 1. Choose the correct route

| Intent | Start here |
|---|---|
| Use or understand Gradle Actions | `README.md` and `docs/` |
| Audit inherited rights/provenance | `LICENSE` + `THIRD_PARTY_PROVENANCE.md` |
| Inspect the local freestanding experiment | `freestanding/kernel4/README.md` |
| Inspect the Kernel4 gate | `.github/workflows/ci-kernel4-freestanding.yml` + `freestanding/kernel4/ci_gate.sh` |
| Decide a physical/hardware claim | require a separate physical receipt; hosted CI is insufficient |

## 2. Current local delta

PR #3 was merged into `main` on 2026-10-04:

```text
merge commit      = c0a70b7f929b4390c5c8553b6a6a4e03a4274ccc
PR exact head     = 30aeeb5a2ea336ae6d292fe47cbac8db4331a3b5
local surface     = freestanding/kernel4/**
workflow surface  = .github/workflows/ci-kernel4-freestanding.yml
```

The exact PR head had five hosted/software workflows reported successful, including the three-target freestanding gate for x86_64, ARMv7 and AArch64. That evidence does **not** promote physical ARM execution, PMU/cache/thermal/latency measurements, bare-metal firmware execution, or glyph/opcode semantics.

## 3. Rights and authorship boundary

The checked-in repository `LICENSE` is the MIT License with Gradle Inc. copyright notice for the inherited project. `THIRD_PARTY_PROVENANCE.md` correctly preserves upstream authority and forbids whole-repository authorship claims.

The Kernel4 source is evidenced as an independently added local delta, but its files do **not** currently carry a separate SPDX/license grant. Therefore:

```text
INHERITED_GRADLE_ACTIONS_LICENSE = MIT / checked-in LICENSE and applicable notices
LOCAL_KERNEL4_AUTHORSHIP         = evidenced local contribution
LOCAL_KERNEL4_SEPARATE_LICENSE   = TOKEN_VAZIO
WHOLE_REPOSITORY_AUTHORSHIP      = false
```

Do not invent a custom license for Kernel4 and do not reinterpret the inherited MIT grant. If a distinct license for the separable local delta is desired, that is a separate rights decision and must be made explicitly, compatibly, and at file/path level.

## 4. Evidence boundary

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
IMPLEMENTED_UNTESTED != PASS
CI_PASS != PHYSICAL_PASS
TOKEN_VAZIO != 0
```

Kernel4 currently proves a bounded hosted build/link/reproducibility surface. It does not turn the Node/Gradle GitHub Action into freestanding software, and it does not make the inherited Gradle implementation locally authored.

## 5. Reconstruction route

1. For inherited behavior, read upstream-oriented `README.md`/`docs/` first.
2. For a local change, resolve `THIRD_PARTY_PROVENANCE.md` before editing inherited paths.
3. Keep Kernel4 work under `freestanding/kernel4/**` unless an evidenced interface requires otherwise.
4. Bind every execution claim to exact source SHA and receipt.
5. Keep physical/hardware evidence in a separate gate from hosted CI.
6. Before release or redistribution, resolve file-level license obligations for every local or bundled delta.

## 6. Open gaps

```text
PHYSICAL_ARM32_SAME_ARTIFACT = TOKEN_VAZIO
PHYSICAL_ARM64_SAME_ARTIFACT = TOKEN_VAZIO
PMU_CACHE_THERMAL_LATENCY    = TOKEN_VAZIO
GLYPH_OPCODE_SEMANTICS       = TOKEN_VAZIO
LOCAL_KERNEL4_SEPARATE_LICENSE = TOKEN_VAZIO
```

R3=<F_ok: inherited Gradle route, local Kernel4 route and rights boundary are separated, F_gap: physical/hardware/glyph evidence plus separate local-delta license remain TOKEN_VAZIO, F_next: keep runtime work separate; resolve rights only by explicit file-level decision and physical claims only by exact-artifact receipts>
