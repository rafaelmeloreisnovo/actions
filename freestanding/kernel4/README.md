# Kernel4 freestanding core

Status is determined only by source-bound CI evidence. `IMPLEMENTED_UNTESTED != PASS` and `CI_PASS != PHYSICAL_PASS`.

## Intent

Materialize the demonstrated structural invariant:

```text
(4bit | 4bit) -> 8-bit frame
```

as a minimal freestanding core that is independent of the inherited Gradle/Node runtime.

## Provenance boundary

- `SOURCE`: the user-supplied `(4bit|4bit)` frame structure.
- `ARTIFACT`: `kernel4.c` + `kernel4.ld` + `ci_gate.sh` + CI receipt.
- `EXECUTION`: exact-source Clang/LLD cross-linking performed by GitHub Actions.
- `EVIDENCE`: ELF identity, entrypoint, sections, segments, stack use, size, two-build reproducibility and SHA-256 receipt.
- `CLAIM`: only the local Kernel4 delta is RAFAELIA-authored. Inherited Gradle Actions content remains third-party under `THIRD_PARTY_PROVENANCE.md`.

The inner emoji/glyph sequence has **no assigned machine opcode in this version**. Its operational mapping is `TOKEN_VAZIO`, deliberately preventing symbolic interpretation from being presented as implemented behavior.

### `TOKEN_VAZIO != 0`

Unknown/unauthorized glyph payloads are represented by **absence of a value**, not by assigning the numeric value zero:

```text
cell.present = 0  => payload absent / ignore cell.value
cell.present = 1  => cell.value is an authorized 8-bit frame
```

Therefore these states are distinct:

```text
TOKEN_VAZIO        => present=0, no semantic numeric value
known frame 0x00   => present=1, value=0x00
```

The eight current glyph rows are structurally present but their machine payloads remain absent until an explicit opcode authority is defined.

## Contract

The core must compile/link with:

- `-ffreestanding`
- `-fno-builtin`
- `-fno-stack-protector`
- `-fno-pic -fno-pie`
- unwind tables disabled
- `-nostdlib` by construction at link time (direct `ld.lld`)
- no libc
- no heap
- no syscalls
- no host I/O
- no dynamic loader
- no dynamic dependencies
- no undefined external symbols
- no runtime relocations
- no writable+executable load segment
- no executable stack
- no stack use before a stack bootstrap exists

The CI builds three independent ELF images:

1. `x86_64-unknown-none-elf`
2. `armv7-none-eabi`
3. `aarch64-none-elf`

The `x86_64` profile also disables the red zone. ARM profiles remain architecture-generic; hardware-specific performance tuning is not promoted until physical-device receipts exist.

## Kernel shape

```text
high nibble  H4 = bits 7..4
low nibble   L4 = bits 3..0
frame        V8 = H4 || L4
parity       P2 = parity(H4) || parity(L4)
rows         R8 = 8 structural cells
validity     M8 = one presence bit per row
```

`P2` is metadata calculated from a known frame; it does not expand `V8` into a 10-bit address space. `M8` is evidence metadata that keeps unknown rows distinct from a known zero frame.

## Critical CI gate V2

`freestanding/kernel4/ci_gate.sh` is the local, reproducible gate used by CI and can also be invoked outside GitHub Actions when the same toolchain is available.

A target passes only when all checks hold:

```text
source SHA            = expected source SHA
ELF class/machine     = expected architecture
ELF type              = EXEC
entrypoint             = kernel4_entry
NEEDED                 = NONE
INTERP                 = NONE
UNDEFINED              = NONE
runtime relocations    = NONE
runtime-oriented sect. = NONE
W+X LOAD segment       = NONE
executable stack       = NONE
max stack bytes        = 0
allocated image        <= 4096 bytes
build A == build B     = byte-for-byte identical
SHA-256                = RECORDED
```

The 4096-byte allocation ceiling is a deliberate critical-core ratchet. Increasing it requires an explicit contract change rather than silent growth.

## Friction and supply-chain controls

The lane now:

- uses a fixed `ubuntu-24.04` runner contract instead of `ubuntu-latest` drift;
- resolves the already installed versioned LLD (`ld.lld-18` when needed) and **does not run `apt-get`**;
- checks out only the Kernel4 subtree;
- checks the PR source head explicitly and records source/event/base SHAs separately;
- pins external GitHub actions by immutable commit SHA;
- cancels obsolete runs from the same PR/ref;
- stores 30-day evidence artifacts with no compression overhead for these tiny files;
- emits a compact job summary plus a machine-friendly key/value receipt.

No CI result promotes physical ARM32/ARM64 execution, hardware performance, glyph semantics, or the hosted Gradle/Node action into a freestanding claim. Those remain separate evidence gates.
