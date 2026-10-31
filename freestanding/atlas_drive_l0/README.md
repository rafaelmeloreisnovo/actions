# RAFAELIA Atlas/Drive L0 — bounded freestanding planner

**Status:** CANDIDATE / PLAN_ONLY / `claim_allowed=false` / DRAFT-HOLD.

This is an isolated, independently added candidate under the local `freestanding/` lane of a fork of `gradle/actions`. It does **not** replace Gradle Actions, `kernel4`, `dispatch_l0`, `omega_os`, `apk_bridge`, source trees or any private producer. File-level provenance and redistribution rights require separate review; see `LICENSES/README.md` and the root `THIRD_PARTY_PROVENANCE.md`.

## What is implemented

- One exported freestanding C11 function, `ra_atlas_plan`, with caller-provided input and output. No libc, heap, malloc, syscalls, file I/O, network, TLS, Java, DEX, JNI, Android framework, Python, JSON parser or global mutable state in the L0 implementation.
- Fixed batch `RA_MAX=16` with bounded O(n²) duplicate detection. All copies of a duplicate key are held; no first-writer-wins bias. Known zero and missing attestation have different types.
- Per-record source identity/revision/target and typed `kind`, seven relation IDs (direct, inverse, derived, antiderived, recursive, orthogonal, integrative), public/private scope and eight gap states (none + seven typed unknown categories).
- Source/provenance/rights/destination attestation masks supplied by an **independently trusted caller**. The C module cannot verify an assertion. Missing attestation or nonzero gap is held, never inferred away.
- Monotone sequence / stale-replay rejection; external TTL `elapsed >= ttl` rejection; two caller-provided watchdog bounds. No timer is run and no watchdog independence is proven.
- Deterministic plan states: `PLAN_ONLY`, `PARTIAL`, `HOLD`, or typed global errors. No Drive or GitHub mutation, no publication or merge permission: output `drive_writes=publish_authorized=claim_allowed=0` for all paths.
- CRC-32C over the ordered normalized plan decisions and types, excluding source IDs and revisions. **This is not authentication, encryption, a content hash or evidence of Drive persistence.** Do not publish low-entropy or sensitive derived metadata as a privacy guarantee.

## Why this module, rather than a rewrite

The authoritative Drive dispatch is `CURRENT_STATE -> START HERE V2.2 -> SOURCE_MIN -> AUTHORITY -> ACT -> EVIDENCE -> muWRITE -> R3`. The current Gradle Actions fork already contains C11 candidates `dispatch_l0`, `kernel4`, `omega_os`, and `apk_bridge`. Reusing their tested design boundaries is less risky than changing inherited Node/Gradle code. The planner never reads other repos; it accepts records from the trusted host only. It creates no external scalable services and does not run in the background.

## Reproduce host-only tests

```sh
sh freestanding/atlas_drive_l0/tests/verify.sh
```

The host harness has 20 explicit failure codes (empty batches are held as RA_MISSING) (valid plan, stable CRC, null input, missing proof, stale sequence, watchdog, TTL, rights, withheld, public/private boundary, duplicate keys, partial plan, invalid relation, oversized batch, missing type, absent key, unknown attestation bit, overflow replay, empty plan, invalid visibility), run at `-O0` and `-O2`. Three separate target objects (`x86_64-unknown-none-elf`, `armv7-none-eabi`, `aarch64-none-elf`) are compiled under `-ffreestanding -fno-builtin` and checked for undefined symbols. A host toolchain is necessary for *building and testing*, but is **not linked into the L0 object**.

An executable host test is **not** ARM device execution; successful cross-object compilation is **not** an APK, loadable JNI library or signed installer. Refer to existing `freestanding/apk_bridge/README.md` for the Android build boundary.

## Drive/Android data plane — proposed contract, NOT implemented

```text
Official Drive OAuth (trusted Android / OS-backed boundary, approved scopes)
  -> list metadata/changes via trusted client, bounded batches (<=16)
  -> private-only content handling where explicitly authorized
  -> host verifies source id/revision, rights, byte SHA-256, destination permission
  -> Atlas L0 PLAN_ONLY: typed route/hold/gap, monotone sequence, TTL checks
  -> host prepares append-only metadata patch and reviewable proposed diff
  -> Drive conditional write (revision/ETag), then independent READBACK
  -> private receipt + supersedes/rollback pointer in authorized Drive ledger
```

Never place refresh tokens, PATs, private formulas, raw chat shards, OAuth verifier, private SHA of low-entropy content or Drive credentials in the public repository, public GitHub Actions artifact, APK assets or its logs. Public GitHub CI uses synthetic fixtures only. A compiler or zip packer does not implement TLS/OAuth. Google APIs, Android OS facilities and hardware drivers are **external platform boundaries**, not freestanding CPU instructions. The mobile device is an on-demand compute client; **Drive is persistence, not RAM/cache**, and transient bounded buffers on device remain necessary.

## Operational gates

| Gate | Required result | Current state |
|---|---|---|
| L0 source | fixed memory, no libc and no unresolved object symbols | local host tests; exact GitHub CI pending |
| Negative falsifiers | reject replay/TTL/cross-privacy/duplicates/rights/unknown gaps | local host tests; independent review pending |
| Host adapter | real Drive auth and least-privilege scoped API | TOKEN_VAZIO / NOT_IMPLEMENTED |
| Drive commit | revision-protected append-only write + readback receipt | TOKEN_VAZIO / NOT_EXECUTED |
| Android ABIs | physical ARM32 + ARM64 ELF loading on devices | TOKEN_VAZIO / NOT_EXECUTED |
| APK | DEX/Manifest/resources/ZIP signing/verify/install + wizard | TOKEN_VAZIO / NOT_BUILT |
| Hardware | NEON/CRC instruction flags, GPU, NUMA discovery/measurement | TOKEN_VAZIO / NOT_MEASURED |
| Security/privacy | threat model, independent review, rights/scope and canary | TOKEN_VAZIO / NOT_TESTED |

**Decision:** no GPU, NUMA, SIMD, NEON or hardware CRC instruction is used by this planner. Modern Android may expose some but access must be discovered by the OS and measured per device and ABI. Scalar operations remain the reference path; SIMD can only replace it after output-equivalence and side-channel/privacy tests. Some Android phones have no useful NUMA support and L3 is not guaranteed. Branchless control flow is not a general safety or performance guarantee.

**Compression:** ZIP, Huffman, and ZIPRAF are separate codecs with exact round-trip and integrity gates. Claims of reconstructing data after deliberately deleting 25–45% of arbitrary bits require explicit redundancy and a recoverability model; neither CRC-32C nor this planner provides error correction. No data loss is authorized.

**R3:** `F_ok=isolated candidate + bounded falsifiers`, `F_gap=real Drive/Android permissions, rights, devices and independent verification`, `F_next=approved synthetic Drive adapter and conditional-write/readback canary in private scope`. Rollback: close draft PR; main, Drive files and private sources remain unchanged.
