# Platform matrix: source vs object vs runtime vs verified boot

This is a forward architecture, not a completed multi-OS emulator.

Target | L0 source | Exact-target object | Guest OS runtime | Boot
---|---|---|---|---
x86_64-none | C11 source | CI pending | NOT_RUN | NOT_APPLICABLE
ARMv7-none | C11 source | CI pending | NOT_RUN_PHYSICAL | NOT_APPLICABLE
AArch64-none | C11 source | CI pending | NOT_RUN_PHYSICAL | NOT_APPLICABLE
Linux host | hosted tool adapter | existing tools required | NOT_RUN_APP | NOT_APPLICABLE
FreeBSD | plausible C11 source | NOT_RUN | NOT_RUN | NOT_APPLICABLE
OpenBSD | plausible C11 source | NOT_RUN | NOT_RUN | NOT_APPLICABLE
Generic Unix | ABI unresolved | NOT_RUN | NOT_RUN | NOT_APPLICABLE
OpenDOS/DOS | 16-bit ABI/segment model unresolved | NOT_RUN | NOT_RUN | NOT_APPLICABLE
Android | official SDK tool adapter | NOT_RUN_APK | NOT_RUN_INSTALL | OEM_CONTROLLED
RAFAELIA virtual machine | toy bytecode | host synthetic tests pending | TOY_ISA_ONLY | NO_CRYPTO

Roadmap, in separate reviewed producer scopes:
1. Explicit ABI/syscall/stack/linker profiles for each target, source-side falsifiers.
2. Freestanding binary parser and cross-ISA consumers, fuzz/ASan/UBSan host gates.
3. Incrementally replace Android build components only with reproducible byte or
   semantic parity to trusted AAPT2/D8/zipalign and Android signing tools.
4. Virtual firmware boot under QEMU with signed image manifest and antirollback.
5. Independent device-specific recovery/rights/OEM authority before any real boot.

Failure types: TOOLCHAIN_MISSING, RIGHTS_TOKEN_VAZIO, ABI_UNRESOLVED,
SOURCE_ONLY, OBJECT_ONLY, APK_BUILD_NOT_RUN, APK_SIGN_NOT_RUN,
DEVICE_NOT_RUN, BOOT_CRYPTO_NOT_IMPLEMENTED, PROVIDER_ENFORCEMENT_UNVERIFIED.
Earlier PASS cannot promote later stages.
