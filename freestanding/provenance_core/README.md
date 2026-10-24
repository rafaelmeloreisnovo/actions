# RAFAELIA — Independent provenance decision core

This is a **new, isolated local C11 implementation** drafted from a rights/evidence contract, not a rewrite or rebranding of upstream Gradle Actions code. No Gradle, Node, libc, heap, system call or host I/O is referenced in the freestanding C translation unit. The test harness is hosted and is not part of the freestanding runtime.

## Responsibility boundary

`rights_core.h` declares a deliberately finite contract; `rights_core.c` evaluates **asserted bits**, not truth or legal title. The caller must independently prove source revision, per-file digest, rights holder, license scope, attribution, exact-head software test, and independent review. Otherwise it must leave the relevant bit clear. There is no signature verification or copyright infringement detection.

Statuses: UNKNOWN (0), BAD_INPUT (1), RIGHTS_GAP (2), EVIDENCE_GAP (3), STRUCTURAL_CANDIDATE (4). Origins: UNRESOLVED (0), INHERITED (1), LOCAL (2), MIXED (3). MIXED always blocks and needs file-level decomposition. Known numeric zero is a real value; missing proof is an unset bit, not a numerical approval.

`release_authorized` is **unconditionally zero**. Even state 4 is not a license, publication permission, actual CI PASS, legal novelty determination, or authority to merge. Attribution and applicable MIT notices in the parent fork stay untouched.

## Reproduce the bounded local test

```sh
python3 -m unittest discover -s freestanding/provenance_core/tests -p 'test_*.py' -v
```

Eight hosted unit test methods cover unknown origins, invalid flags, missing credits, rights-before-evidence precedence, release block and cross-object compilation for x86-64/ARMv7/AArch64. Requires Clang and nm on the host. No physical ARM, runtime loader, or provider controls are tested.

## Authorship and relocation

This code was authored for the user's requested separate local RAFAELIA lane on 2026-10-24. See `AUTHORSHIP_AND_CREDITS.md` and `provenance/lineage.v1.json` for repository boundaries and unresolved holder/grant checks. Separate proprietary upstream content must never be recharacterized as original. Relocating into a dedicated RAFAELIA producer repository is a future reviewed change.

R3 = <F_ok: isolated source + falsifiers, F_gap: human attestation/license/per-file lineage/exact-head CI/independent review, F_next: exact-head hosted gate and file-level legal audit>.

## Follow-up hardening (2026-10-24)

Input/receipt buffer overlap is supported by snapshotting two words before any output write. This changes only the deterministic interpretation of a shared caller buffer, not the release barrier. Ten hosted Python test methods include a 256-case claim truth table, 25 invalid high-bit masks, null and alias fixtures; a separate host-only C falsifier runs under AddressSanitizer/UBSan. None of these prove a copyright entitlement or executable physical ARM behavior. For wider risk controls see `../../governance/RISK_REGISTER_20261024.md`.
