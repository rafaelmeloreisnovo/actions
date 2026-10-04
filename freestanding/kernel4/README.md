# Kernel4 freestanding core

Status: `IMPLEMENTED_UNTESTED` until the repository CI for the exact commit is green.

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
rows         R8 = 8 structural frames
```

`P2` is metadata calculated from a frame; it does not expand `V8` into a 10-bit address space.

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

`IMPLEMENTED_UNTESTED != PASS`.
