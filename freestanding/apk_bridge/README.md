# RAFAELIA — Freestanding APK bridge and synthetic boot

PROPOSAL ONLY. Claim policy: SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
IMPLEMENTED_UNTESTED != PASS. CI_PASS != PHYSICAL_PASS. TOKEN_VAZIO != 0.

## Architectural separation

L0 apk_probe.c: independently added freestanding C11 ZIP32/APK structural parser.
L0 boot_vm.c: independently added bounded synthetic bytecode interpreter.
L1 host/build_debug.sh: hosted adapter to an EXISTING Android Gradle project.
L2 FreeBSD/OpenBSD/Linux/Unix/DOS ABI adapters and hardware boot: NOT IMPLEMENTED.

Inherited Gradle Actions source, MIT license and THIRD_PARTY_PROVENANCE.md
remain authoritative. Authorship is limited to the local delta, not the fork.
A separately licensed right of redistribution for this local delta has not
yet been resolved (TOKEN_VAZIO_LICENSE); no new license is asserted.

## What runs and what does not

APK probe: caller provides entire readable buffer, length limited to
32-bit unsigned, maximum 8192 central directory records. Structural subset
checks ZIP32 EOCD and central/local offsets, filename consistency, compression
method 0/8, traversal, archive boundaries and root AndroidManifest.xml.
Result status 0 only means STRUCTURAL_ZIP32_SUBSET; it does not authenticate a
signature, verify CRC/decompression, inspect AndroidManifest content or DEX,
check alias/entry overlaps, install an APK or establish validity on Android.
ZIP64, encryption and multidisk are rejected; status codes type failures.

Toy boot VM: finite fuel, four 8-bit registers, no host I/O/syscalls. Bytecode
0x00 HALT, 0x10-13 LOAD next byte into register, 0x20-23 XOR register into r0,
0x30-33 ADD register into r0 modulo 256. This is NOT an ARM/x86 emulator,
FreeBSD/Linux guest, firmware, bootloader or hardware execution claim.

Compile native host test shim (this .so is hosted and NOT deployable as L0):
    clang -std=c11 -O2 -fPIC -shared -ffreestanding -fno-builtin \
      freestanding/apk_bridge/apk_probe.c freestanding/apk_bridge/boot_vm.c \
      -o freestanding/apk_bridge/libra_bridge.so
    RA_BRIDGE_TEST_LIB=freestanding/apk_bridge/libra_bridge.so \
      python3 -m unittest discover -s freestanding/apk_bridge/tests -v

A GitHub workflow cross-compiles freestanding OBJECTS for x86_64, ARMv7 and
AArch64 and checks for undefined references. Object build PASS does not
establish executable ELF, ABI parity, physical runtime or OS compatibility.

## Real debug APK hosted adapter

Requires a real Android application project, gradlew, an already provisioned
Gradle distribution/dependencies, JDK, Android SDK and command-line zipalign
and apksigner. Nothing is downloaded by this adapter; --offline fails closed
when caches/tools are incomplete.

    bash freestanding/apk_bridge/host/build_debug.sh \
      /path/to/android/project app/build/outputs/apk/debug/app-debug.apk

The script builds :app:assembleDebug, checks the resulting APK using official
zipalign and apksigner, and emits SHA-256 with a narrowly scoped receipt.
The official Android toolchain still creates Java classfiles, DEX, resources,
and APK signatures. No authorial Java compiler, AAPT2, D8/R8, or secure v2/v3/v4
signer is claimed. This repo does not contain the app source, so it cannot
produce a real APK independently. Signing keys must not be committed.

Real manual signing stages: package -> align -> sign -> verify -> immutable
artifact. Changing APK bytes after signing invalidates signature. Verify
signed APKs with Android apksigner, not with the structural C parser.

## Boot policy

Android Developer Options do NOT imply permission to replace a bootloader.
OEM unlock capabilities are device-specific and may erase data. Verified Boot
requires device trust chain, cryptographic image integrity and rollback policy.
This change contains NO fastboot, flash, partition writer or device-modifying
instruction. Later work may use an isolated QEMU virtual platform with its own
tests/verified boot design, then seek explicit consent for hardware stages.

## Gate and promotion

Current status before exact-head CI: IMPLEMENTED_UNTESTED.
Block promotion while independent review, file-level rights, real APK
consumer/build proof, signatures, provider enforcement or physical targets
remain TOKEN_VAZIO. A draft PR must not be merged merely because compilation
passes. Rollback: close the draft PR; main remains untouched.

## 2026-10-24 ambiguity falsifier (source-only delta)

This bounded L0 subset explicitly returns `RA_AMBIGUOUS_CRITICAL=9` if a ZIP
central directory contains more than one exact root `AndroidManifest.xml` or
`classes.dex` entry. Unknown/unsupported data and ambiguity must not be
promoted to a trusted installable APK. This **does not** authenticate ZIP
contents, detect duplicate arbitrary paths, inspect DEX, verify CRC/decompress,
check arbitrary aliasing/overlaps or replace `apksigner`.

Reproducibility at the candidate source: 19 historical host tests remained
PASS; three additional ambiguity boundary tests PASS (22/22), using the
existing freestanding Clang compilation for x86_64, ARMv7 and AArch64 with
zero undefined object symbols. Local software evidence is distinct from an
exact PR-head GitHub Actions receipt or physical Android execution.
