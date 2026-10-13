# Machine contracts / risk gates for Ω-OS v0.1

Authority and boundary:
- SOURCE: Omega kernel new subtree in actions fork (experimental incubation)
- AUTHORITY: local independent delta only; inherited Gradle/Node rights intact
- EXECUTION_TARGET: hosted synthetics + x86_64/ARMv7/AArch64 object probes
- EVIDENCE_RULE: exact source SHA, test counts, sanitizer receipt, undefined
  symbols, negative transitions, deterministic replay; provider runs by SHA

Typed state/knowledge:
- O_EMPTY = numeric known enum state 0, **NOT** TOKEN_VAZIO.
- TOKEN_VAZIO_IDENTITY_ATTESTATION: caller-supplied IDs not authenticated.
- TOKEN_VAZIO_STALE_HANDLE: task slot reuse without lifetime/epoch tokens.
- NOT_RUN_PHYSICAL: no ARM32/ARM64 hardware test.
- NOT_IMPLEMENTED_BOOT: BOOT is state transition, not firmware.
- NOT_IMPLEMENTED_PREEMPTION: cooperative schedule only.
- NOT_IMPLEMENTED_ADDRESS_SPACES: no MMU/security boundary.
- NOT_IMPLEMENTED_INTERRUPTS: none registered or dispatched.
- NOT_IMPLEMENTED_PERSISTENCE: receipts returned, never stored by core.
- NOT_IMPLEMENTED_CRYPTOPROOF: FNV32 is NOT cryptographic.
- NOT_IMPLEMENTED_APP_EXECUTION: tasks are state slots, not executable payload.
- NOT_RUN_ANDROID: APK build adapter belongs to separate draft PR#6.
- TOKEN_VAZIO_RIGHTS: new file-level grant not approved by owner.
- TOKEN_VAZIO_PROVIDER_ENFORCEMENT: branch rules and independent review
  must be verified on host provider before merge.

Falsifiers:
F01 bad/forged actors reject; F02 stale/reordered sequence reject;
F03 no slot transitions from illegal phases; F04 grant cannot self-escalate;
F05 rejected events leave context bitwise identical; F06 one RUNNING task;
F07 deterministic schedule and replay; F08 bounded capacity and overflow;
F09 shutdown blocked by active tasks; F10 capabilities cleared on REAP;
F11 compiler no undefined symbols on three object targets;
F12 host ASan/UBSan adversarial 30000 events.

Release/promotion matrix:
SOURCE_READBACK -> OBJECT_BUILT -> HOST_FALSIFIERS -> VIRTUAL_BOOT ->
PHYSICAL_BOOT -> INDEPENDENT_REVIEW -> RIGHTS -> PROVIDER_ENFORCEMENT -> CLAIM
Each gate independent; no forward inference, automatic promotion, or merge.
ROLLBACK: close draft PR with no changes to main, supersede ledger entry.
