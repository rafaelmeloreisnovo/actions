# Termux producer → Actions dispatch L0 | scoped CI boundary

## Source authority and routing

- Producer A: `rafaelmeloreisnovo/actions`, `freestanding/dispatch_l0/{dispatch.c,dispatch.h,tests/verify.sh}`; native decision has no external symbols, libc, heap, I/O or syscall calls.
- Provider gate: `.github/workflows/ci-rafaelia-dispatch-l0.yml`, which checks out the exact full source SHA with Git transport and then invokes the **owned** `rafcode/verify-source/action.yml`.
- Producer B: `rafaelmeloreisnovo/termux-packages`; NDK/DEB/ZIP source-build belongs there, not in this fork.
- Producer C: `rafaelmeloreisnovo/termux-app-rafacodephi`; APK/DEX/ART/HTTP device runtime belongs there.
- Attribution: see repository `LICENSE`, `THIRD_PARTY_PROVENANCE.md`, `AUTHORSHIP_AND_CREDITS.md` and local `freestanding/dispatch_l0/LICENSES/README.md`. No license or historical authorship changes.

## Bounded pipeline

```
PR/push source SHA
  → exact detached checkout
  → owned verify-source: Git HEAD + clean tracked tree + index
  → host C falsifiers O0/O2 + undefined-symbol audits
  → ARMv7/AArch64 cross-object checks
  → typed CI evidence, reviewer, provider enforcement
  → no automatic merge or Android release
```

Source identity does **not** verify submodule content trust, ignored/untracked builder inputs, cryptographic signature, physical watchdogs, immutable toolchain provenance or emitted APK hashes. Any missing independent evidence remains `TOKEN_VAZIO`. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

L0 capabilities `scalar/NEON/SIMD/GPU` are caller assertions, not hardware observations; GPU is denied in L0. Two watchdog values are validated **inputs**, not two active timers. ELF object compilation does not imply bootability; DEX/ART and NUMA require separate producers/platforms. No execution, hardware dispatch, failover or rollback is performed by documentation or CI.

## Acceptance, failure and rollback

Acceptance for this delta: workflow parses; `verify-source` passes on the exact HEAD before the preexisting L0 tests; tests still pass; no changes to root Gradle action, production code, licenses, signatures or runtime. On any source mismatch, exit nonzero. A passing CI gate cannot override a missing manual approval, insecure provider rulesets or failed physical device evidence.

Rollback: revert only the additive workflow step on a separate guarded commit; preserve this branch and all predecessor refs. `claim_allowed=false`; `promotion=HOLD`.
