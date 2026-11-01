# RAFAELIA Ω — freestanding entry L0 (independent candidate)

This folder is an isolated **original-candidate** C entry and capability dispatch. The repository remains a fork of `gradle/actions`; no inherited Gradle runtime or source is used **by this directory**. It is NOT a replacement for `gradle/actions`, GitHub Actions, ART, Android runtime, GPU drivers or Linux.

## Entry contract

`rf_execute(request, receipt)` is the only external C function. No libc, malloc/heap, syscalls, Java, JNI, SDK or Gradle in the C core. Callers own memory and authorize any outside effects. The bytewise XOR transform is a **test fixture**, not a production encryption, compression or novel mathematical method. It processes at most 256 bytes, staging output on the stack so errors leave caller destination/receipt unchanged.

`RF_REQUIRE_NEON` chooses a NEON kernel only when compiled for NEON **and** a trusted adapter asserts `RF_CAP_NEON_VERIFIED`; the assertion is not itself proof of available hardware. GPU/NUMA/ART/DEX requests are rejected unless explicit safe scalar fallback is permitted. Two logical watchdog budgets cap units and 16-byte progress blocks; they are not independent hardware watchdogs, timers or thermal protection. No background task, self-directed execution or remote access.

## Architecture and boundaries

```
Optional external Gradle / Termux / CI caller    (not code used by L0)
           | ABI v1 request; source/ref + authority verified by external caller
           v
      entry.h -> entry.c  [bounded CPU scalar / conditional NEON]
           |
           v
         receipt v1 (logical units, backend, fallback, fingerprint)
           |
           v
external host stores SHA256 provenance + device/provider receipts
```

The fingerprint is a noncryptographic diagnostic. No signature is issued. No output I/O, device probe, NUMA, GPU, native Android `.so`, DEX or signed APK is produced here. NativeActivity may be a future **separate** Android adapter with a manifest and native library; no user-authored Java or DEX is required for the pure native activity path, but the Android framework and binary-packaging tools remain third party.

## Tests (scoped)

`sh tests/verify.sh` requires installed `clang`, `nm` and a usable ASan/UBSan host. It executes the host test and only **cross-compiles** ARMv7/AArch64 objects. ARM device execution, NEON runtime-equivalence, GPU and NUMA remain `TOKEN_VAZIO_NOT_TESTED`.

`LICENSES/README.md` tracks separate rightsholder/license gaps without rewriting the inherited root license. No publication or merge until independent reviewer and exact-run receipt; `claim_allowed=false`.

Rollback: close draft PR; source files never modify upstream paths or built distributions. Next: exact-head hosted test, ABI-specific emulator/device receipt, then optional explicit Gradle *invocation-only* adapter in a producer repository outside this fork.
