# RAFAELIA Ω-OS: Original State-Machine Operating System Research

Version: 0.1 — **state-kernel prototype, NOT a complete operating system**.
The user's intent is a new original operating-system architecture governed
by deterministic state transitions and an Omega Orchestrator, rather than
emulation/compatibility with historical Unix, BSD, Linux, DOS or Android.

## Architecture: machine-of-states first

  Omega boot authority (external, currently UNIMPLEMENTED)
      -> typed events / caller-validated identities
      -> Ω finite transition authority
      -> bounded deterministic scheduler
      -> capability grants and revocation
      -> state snapshots + output receipts
      -> FUTURE hardware platform adapters / isolation / memory / drivers
      -> FUTURE Android/Java/APK build consumer (optional, not kernel authority)

All tasks are state objects. Only an explicit event can change state. The
first executable model has 8 slots, no dynamic memory, one writer, one
running slot, a cooperative round-robin selector and no ambient syscall.
No hardware interrupts, CPU context switch or executable task payload.
It **does not run arbitrary programs yet**. It has no Unix process ABI.

## State machine

Lifecycle COLD -> LIVE -> SHUT (one way). BOOT is a logical transition,
not a firmware boot or cryptographic verification. Only supervisor actor
ID 0 may issue BOOT, SPAWN, SCHEDULE, WAKE, FAULT, REAP and SHUTDOWN.
Task identities are 1..8 and are caller supplied; identity **is not
authenticated** by this core. Caller/platform must attest actor IDs, enforce
single-writer serialization and memory/interrupt boundaries.

Slot transitions:

- EMPTY -> READY through privileged SPAWN with explicit grant bits
- READY -> RUNNING through privileged round-robin SCHEDULE
- RUNNING -> READY on authorized YIELD
- RUNNING -> WAITING on authorized WAIT
- WAITING -> READY on privileged WAKE
- READY/RUNNING/WAITING -> STOPPED via authorized EXIT
- READY/RUNNING/WAITING -> FAULTED via privileged FAULT
- STOPPED/FAULTED -> EMPTY via privileged REAP (capability erased)

Capability grant is limited to RUN=1, CONTROL=2, EXIT=4. Capability changes
require a fresh spawn after REAP. It does not implement secure tokens, actual
CPU privilege separation, sandboxing, memory protection or trusted identities.
No PID reuse protection across lifetimes yet: tasks IDs 1..8 are recycled;
external callers MUST prevent stale actor handles (typed gap).

Accepted event sequence starts at 1, is strictly monotonic; overflow blocks
all changes. An invalid event is rejected atomically (no state mutation),
returns a typed error and an observational receipt. Accepted receipts contain
a rolling FNV32 digest for regression/determinism only; it is **not a
cryptographic hash, MAC, signature, anti-rollback or audit chain**. Persistent
storage and trustworthy audit receipts are responsibilities of a future
verified boot/host platform adapter. Rejected events are not appended inside
the core; caller MUST persist rejection receipts when audit is required.

## Build and verify in a hosted laboratory

Run source-side host falsifiers:

    clang -std=c11 -O2 -Wall -Wextra -Werror -ffreestanding -fno-builtin \
      -fPIC -shared freestanding/omega_os/omega_core.c \
      -o freestanding/omega_os/libomega.so
    OMEGA_TEST_LIB=freestanding/omega_os/libomega.so \
      python3 -m unittest discover -s freestanding/omega_os/tests -p 'test_*.py' -v

Independent sanitizer harness:

    clang -std=c11 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
      -Wall -Wextra -Werror freestanding/omega_os/omega_core.c \
      freestanding/omega_os/tests/fuzz_host.c -o /tmp/omega_fuzz
    /tmp/omega_fuzz

CI object-compiles the source for x86_64, ARMv7 and AArch64 with
-ffreestanding -fno-builtin -fno-stack-protector, then checks undefined
symbols. Object compile is not an OS boot, task runtime, physical hardware
validation or freestanding linked image. Hosted fuzz/Python link against
system runtimes only in the **test harness**, not in the kernel source.

## Program evolution and hard gates

P0 — SOURCE / rights / separate repo authority: the parent
rafaelmeloreisnovo/actions is an inherited gradle/actions fork. This
isolated subtree is a proposal, not a statement of whole-fork ownership.
Rehome to a dedicated first-party Omega-OS producer repository before
OS release. Exact copyright/license grant of this local delta: TOKEN_VAZIO.

P1 — MACHINE PROOF: exhaustive legal transitions and rejected transitions;
source-bound executable CI; deterministic replay; independent reviewer;
race-free external event serialization; repair stale-handle/identity model.

P2 — COMPUTE: caller-owned task code, safe CPU context bootstrap, trap/IRQ
delivery, preemption with explicit state transitions, bounded queues,
memory isolation/MMU and privilege boundary in CPU hardware.

P3 — STORAGE & INTEGRITY: transactional state snapshots with recoverable
hash-chains/Merkle via audited cryptographic library; measured secure boot,
rollback protection, trusted key ownership, least privilege / zero trust.

P4 — VIRTUAL BOOT: architecture-specific linker/ELF/boot image and isolated
QEMU VM physical-ABI contract; signed image verification and recovery gate.
The kernel currently has **no executable bootloader**. Android Developer
Options do not unlock hardware firmware.

P5 — APPLICATION PLATFORM: native executable format, compiler/linker,
sandboxed capability-mediated I/O and optional Android/Dex/Java compatibility
or APK publishing bridge. None is implemented by this prototype.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
TOKEN_VAZIO != 0; IMPLEMENTED_UNTESTED != PASS; CI_PASS != PHYSICAL_PASS.
No merges while review/rights/provider enforcement and proof gates remain open.
