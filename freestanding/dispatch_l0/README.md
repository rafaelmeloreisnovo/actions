# RAFAELIA Dispatch L0 — deterministic candidate selector

**Status:** SOURCE_CANDIDATE / LOCAL_HOST_TEST_ONLY / CLAIM_ALLOWED=false / PROMOTION=HOLD.

New isolated component under `freestanding/` of the `rafaelmeloreisnovo/actions` fork, NOT a replacement for Gradle Actions, Kernel4, omega_os, rights_core, rafcode, apk_bridge or any device driver. Exactly one exported C function, `rd_plan`, one caller-owned request, one caller-owned receipt; fixed-width uint assumptions asserted. No libc, heap, I/O, syscalls, time, thread, dispatch side-effects or external runtime symbols inside `dispatch.c`. Branches are explicit safety checks; removing control flow does not improve safety by itself.

## Byte/field design

Request: ten 32-bit words: tag, sequence, previous_sequence, present_mask, observed_caps, permitted_caps, preferred, watchdog_a, watchdog_b, watchdog_limit. Receipt: six words: status, route, fallback, rollback_required, hardware_activated, merge_authorized. Native ABI alignment must be independently checked for all targets.

- `RD_TAG = RDL0 (0x52444c30)`, monotonically advancing sequence required. Overflow/replay -> `RD_STALE`.
- `RD_ALL_PRESENT=31` requires explicit knowledge of capability snapshot, policy, watchdog A, watchdog B, source-binding claim. Missing mask bits -> `RD_UNKNOWN`, **not a known zero**.
- Capability bitset: scalar=1, NEON=2, SIMD(other)=4, GPU=8. Bits are assertions from the host, **not CPUID/HWCAP/NUMA hardware discovery**. `eligible = observed & permitted & 7` excludes GPU.
- Preferred NEON/SIMD/scalar when allowed; bounded scalar fallback when preferred unavailable and scalar allowed; default preference NEON then SIMD then scalar. Explicit GPU preference returns `RD_GPU_BOUNDARY`, never silently executes GPU. Fallback is a suggested route, not a failover actually performed.
- Double watchdog *input thresholds* are independently required, positive and <= host-provided bound. They do not tick, preempt, watch execution or prove signal independence. Invalid -> `RD_WATCHDOG`/rollback_required=1. Host must independently attest watchdog freshness and permissions.
- `RD_PLAN_ONLY` (6) is **not a permission or attestation**. `hardware_activated=0` and `merge_authorized=0` unconditionally. Denied paths expose a rollback recommendation, **not an executed rollback**.
- Null receipt guards before dereference; all input words snapshotted before output writes; caller alias supported on tested native ABI.

## Artifact boundaries

`SOURCE` = C + header + review of `LICENSES/`. `ARTIFACT` = per-target object built by Clang host. `EXECUTION` = hosted C harness (not the ARM object) / CI only after verified run. `EVIDENCE` = source SHA, object hashes, undefined-symbol scan, hosted test report. `CLAIM` = candidate low-level selector, not freestanding OS, zero trust enforcement, trusted watchdog or device operation.

ELF object compilation does not prove ELF firmware entry/loader; Android DEX/ART requires Android runtime class and bytecode format; NUMA and GPU require privileged OS/driver or trusted platform providers; NEON/SIMD require exact ISA and hardware tests. None are activated by this L0. External host/CI compiler, GitHub Actions runner, Git transport and `nm` are **build/test dependencies** and cannot be removed if using GitHub Actions. No new Action marketplace dependency is introduced by the proposed workflow.

## Verification

Locally, from repository root:

```sh
sh freestanding/dispatch_l0/tests/verify.sh
```

Host test at `-O0` and `-O2` (`HOST_CC=clang` or `HOST_CC=gcc`); cross objects use `CROSS_CC=clang` independently; independent x86_64, ARMv7 and AArch64 freestanding object compilation with no undefined symbols; deterministic two-build object hash. Hosted tests include negative/fallback/alias/watchdog/replay/capability truth matrix (256 combinations). Nothing in this folder is added to any production path or root action interface. Workflow CI must bind to exact PR HEAD and produce a new provider receipt before approval.

## R3

F_ok = local compiled candidate, tests, per-file git blob SHA. F_gap = source legal clearance, exact-HEAD hosted CI, hardware/ABI device tests, independent reviewer, provider branch protection, actual watchdog authority, verified performance. F_next = exact SHA provider CI, independent review and granted rights; only then consider adapters with separate reversible PRs. Rollback = close DRAFT PR without deleting source branch; no base/main mutation.
