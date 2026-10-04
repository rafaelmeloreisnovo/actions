# Kernel4 freestanding core

Status is determined only by exact-head CI evidence. `IMPLEMENTED_UNTESTED != PASS`.

## Intent

Materialize the demonstrated structural invariant:

```text
(4bit | 4bit) -> 8-bit frame
```

as a minimal freestanding core that is independent of the inherited Gradle/Node runtime.

## Provenance boundary

- `SOURCE`: the user-supplied `(4bit|4bit)` frame structure.
- `ARTIFACT`: `kernel4.c` + `kernel4.ld` + CI receipt.
- `EXECUTION`: Clang/LLD cross-linking performed by GitHub Actions.
- `EVIDENCE`: ELF headers/symbol table/relocations + SHA-256 receipt.
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
- `-nostdlib` by construction at link time (direct `ld.lld`)
- no libc
- no heap
- no syscalls
- no host I/O
- no dynamic loader
- no dynamic dependencies
- no undefined external symbols

The CI builds three independent ELF images:

1. `x86_64-unknown-none-elf`
2. `armv7-none-eabi`
3. `aarch64-none-elf`

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

## CI gate

A target passes the freestanding gate only when all checks hold for the exact ELF produced:

```text
ELF type     = EXEC
NEEDED       = NONE
INTERP       = NONE
UNDEFINED    = NONE
RELOCATIONS  = NONE
SHA256       = RECORDED
```

No CI result promotes physical execution, glyph semantics, or the hosted Gradle/Node action into a freestanding claim.
