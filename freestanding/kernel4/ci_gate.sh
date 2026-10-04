#!/usr/bin/env bash
set -euo pipefail

# RAFAELIA Kernel4 critical freestanding gate.
# Host-side verifier only; a PASS here is not physical-device evidence.

ARCH_NAME=${1:?arch name required}
TARGET=${2:?target triple required}
EXPECTED_CLASS=${3:?expected ELF class required}
EXPECTED_MACHINE=${4:?expected ELF machine required}
ARCH_FLAGS_TEXT=${5:-}
OUT=${6:?output directory required}
MAX_ALLOC_BYTES=${MAX_ALLOC_BYTES:-4096}
EXPECTED_SOURCE_SHA=${EXPECTED_SOURCE_SHA:-}
EVENT_SHA=${EVENT_SHA:-}
BASE_SHA=${BASE_SHA:-}

export LC_ALL=C
export LANG=C
export TZ=UTC
umask 022

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

resolve_tool() {
    local candidate
    for candidate in "$@"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

CLANG_BIN=$(resolve_tool clang clang-18) || fail 'clang toolchain unavailable'
LLD_BIN=$(resolve_tool ld.lld ld.lld-18 lld) || fail 'LLD unavailable; runner mutation/network install is intentionally forbidden'
READELF_BIN=$(resolve_tool readelf llvm-readelf llvm-readelf-18) || fail 'readelf unavailable'
NM_BIN=$(resolve_tool nm llvm-nm llvm-nm-18) || fail 'nm unavailable'
SIZE_BIN=$(resolve_tool size llvm-size llvm-size-18) || fail 'size unavailable'
SHA256_BIN=$(resolve_tool sha256sum) || fail 'sha256sum unavailable'
CMP_BIN=$(resolve_tool cmp) || fail 'cmp unavailable'

read -r -a ARCH_FLAGS <<< "$ARCH_FLAGS_TEXT"

SOURCE_SHA=$(git rev-parse HEAD)
if [[ -n "$EXPECTED_SOURCE_SHA" && "$SOURCE_SHA" != "$EXPECTED_SOURCE_SHA" ]]; then
    fail "checked out SHA $SOURCE_SHA != expected source SHA $EXPECTED_SOURCE_SHA"
fi
export SOURCE_DATE_EPOCH
SOURCE_DATE_EPOCH=$(git show -s --format=%ct HEAD)

build_one() {
    local dir=$1
    mkdir -p "$dir"

    "$CLANG_BIN" \
        --target="$TARGET" \
        "${ARCH_FLAGS[@]}" \
        -std=c11 \
        -Os \
        -ffreestanding \
        -fno-builtin \
        -fno-stack-protector \
        -fomit-frame-pointer \
        -fno-pic \
        -fno-pie \
        -fno-unwind-tables \
        -fno-asynchronous-unwind-tables \
        -fdata-sections \
        -ffunction-sections \
        -fstack-usage \
        -Wall -Wextra -Werror \
        -c freestanding/kernel4/kernel4.c \
        -o "$dir/kernel4.o"

    "$LLD_BIN" \
        --fatal-warnings \
        --no-undefined \
        --gc-sections \
        --build-id=none \
        -z noexecstack \
        -T freestanding/kernel4/kernel4.ld \
        -o "$dir/kernel4.elf" \
        "$dir/kernel4.o"
}

rm -rf "$OUT"
mkdir -p "$OUT"
build_one "$OUT/build-a"
build_one "$OUT/build-b"

ELF_A="$OUT/build-a/kernel4.elf"
ELF_B="$OUT/build-b/kernel4.elf"
STACK_FILE="$OUT/build-a/kernel4.su"
RECEIPT="$OUT/receipt.txt"
FINAL_ELF="$OUT/kernel4.elf"

[[ -f "$STACK_FILE" ]] || fail 'compiler did not emit stack-usage evidence'
"$CMP_BIN" -s "$ELF_A" "$ELF_B" || fail 'two clean builds are not byte-for-byte reproducible'
cp "$ELF_A" "$FINAL_ELF"

ELF_CLASS=$("$READELF_BIN" -h "$FINAL_ELF" | awk -F: '/Class:/ {gsub(/^[[:space:]]+/, "", $2); print $2; exit}')
ELF_MACHINE=$("$READELF_BIN" -h "$FINAL_ELF" | awk -F: '/Machine:/ {gsub(/^[[:space:]]+/, "", $2); print $2; exit}')
ELF_TYPE=$("$READELF_BIN" -h "$FINAL_ELF" | awk '/Type:/ {print $2; exit}')
ELF_DATA=$("$READELF_BIN" -h "$FINAL_ELF" | awk -F: '/Data:/ {gsub(/^[[:space:]]+/, "", $2); print $2; exit}')
ENTRY_RAW=$("$READELF_BIN" -h "$FINAL_ELF" | awk -F: '/Entry point address:/ {gsub(/[[:space:]]+/, "", $2); print $2; exit}')
ENTRY_SYMBOL_HEX=$("$NM_BIN" -n "$FINAL_ELF" | awk '$3 == "kernel4_entry" {print $1; exit}')

[[ "$ELF_CLASS" == "$EXPECTED_CLASS" ]] || fail "ELF class $ELF_CLASS != $EXPECTED_CLASS"
[[ "$ELF_MACHINE" == "$EXPECTED_MACHINE" ]] || fail "ELF machine $ELF_MACHINE != $EXPECTED_MACHINE"
[[ "$ELF_TYPE" == 'EXEC' ]] || fail "ELF type $ELF_TYPE != EXEC"
[[ "$ELF_DATA" == *'little endian'* ]] || fail "unexpected endianness: $ELF_DATA"
[[ -n "$ENTRY_SYMBOL_HEX" ]] || fail 'kernel4_entry symbol missing'

ENTRY_DEC=$((ENTRY_RAW))
ENTRY_SYMBOL_DEC=$((16#$ENTRY_SYMBOL_HEX))
[[ "$ENTRY_DEC" -eq "$ENTRY_SYMBOL_DEC" ]] || fail 'ELF entrypoint does not resolve exactly to kernel4_entry'

if "$READELF_BIN" -d "$FINAL_ELF" 2>&1 | grep -q 'NEEDED'; then
    fail 'dynamic dependency (NEEDED) found'
fi
if "$READELF_BIN" -lW "$FINAL_ELF" | grep -q 'INTERP'; then
    fail 'program interpreter found'
fi
if "$NM_BIN" -u "$FINAL_ELF" | grep -q .; then
    "$NM_BIN" -u "$FINAL_ELF" >&2
    fail 'undefined external symbol found'
fi
if "$READELF_BIN" -r "$FINAL_ELF" | grep -q '^Relocation section'; then
    fail 'runtime relocations found'
fi

FORBIDDEN_SECTIONS='\.(interp|dynamic|dynsym|dynstr|plt|plt\.got|got|got\.plt|init_array|fini_array|ctors|dtors|tdata|tbss)([[:space:]]|$)'
if "$READELF_BIN" -SW "$FINAL_ELF" | grep -Eq "$FORBIDDEN_SECTIONS"; then
    "$READELF_BIN" -SW "$FINAL_ELF" >&2
    fail 'host/runtime-oriented ELF section found'
fi

if "$READELF_BIN" -lW "$FINAL_ELF" | awk '
    $1 == "LOAD" {
        writable = 0; executable = 0;
        for (i = 2; i <= NF; i++) {
            if ($i ~ /W/) writable = 1;
            if ($i ~ /E/) executable = 1;
        }
        if (writable && executable) bad = 1;
    }
    END { exit bad ? 0 : 1 }
'; then
    fail 'W^X violation: writable+executable LOAD segment found'
fi

if "$READELF_BIN" -lW "$FINAL_ELF" | awk '
    $1 == "GNU_STACK" {
        for (i = 2; i <= NF; i++) if ($i ~ /E/) bad = 1;
    }
    END { exit bad ? 0 : 1 }
'; then
    fail 'executable GNU_STACK found'
fi

MAX_STACK_BYTES=$(awk -F '\t' 'NF >= 2 { v = $2 + 0; if (v > max) max = v } END { print max + 0 }' "$STACK_FILE")
[[ "$MAX_STACK_BYTES" -eq 0 ]] || fail "entry/runtime needs stack bytes ($MAX_STACK_BYTES) but this image has no stack bootstrap"

read -r TEXT_BYTES DATA_BYTES BSS_BYTES ALLOC_BYTES _HEX _FILE < <("$SIZE_BIN" "$FINAL_ELF" | tail -n 1)
[[ "$ALLOC_BYTES" =~ ^[0-9]+$ ]] || fail 'could not parse allocated image size'
(( ALLOC_BYTES <= MAX_ALLOC_BYTES )) || fail "allocated image $ALLOC_BYTES bytes exceeds critical budget $MAX_ALLOC_BYTES"

ELF_SHA_A=$("$SHA256_BIN" "$ELF_A" | awk '{print $1}')
ELF_SHA_B=$("$SHA256_BIN" "$ELF_B" | awk '{print $1}')
SOURCE_SHA256=$("$SHA256_BIN" freestanding/kernel4/kernel4.c | awk '{print $1}')
LINKER_SHA256=$("$SHA256_BIN" freestanding/kernel4/kernel4.ld | awk '{print $1}')

{
    echo 'KERNEL4_FREESTANDING_RECEIPT_V2'
    echo "claim_scope=CI_STRUCTURAL_ONLY"
    echo "arch=$ARCH_NAME"
    echo "target=$TARGET"
    echo "source_sha=$SOURCE_SHA"
    echo "event_sha=${EVENT_SHA:-TOKEN_VAZIO}"
    echo "base_sha=${BASE_SHA:-TOKEN_VAZIO}"
    echo "source_date_epoch=$SOURCE_DATE_EPOCH"
    echo "source_sha256=$SOURCE_SHA256"
    echo "linker_sha256=$LINKER_SHA256"
    echo "clang=$($CLANG_BIN --version | head -n 1)"
    echo "lld=$($LLD_BIN --version | head -n 1)"
    echo "elf_class=$ELF_CLASS"
    echo "elf_machine=$ELF_MACHINE"
    echo "elf_type=$ELF_TYPE"
    echo "entrypoint=$ENTRY_RAW"
    echo "entry_symbol=0x$ENTRY_SYMBOL_HEX"
    echo "text_bytes=$TEXT_BYTES"
    echo "data_bytes=$DATA_BYTES"
    echo "bss_bytes=$BSS_BYTES"
    echo "alloc_bytes=$ALLOC_BYTES"
    echo "alloc_budget_bytes=$MAX_ALLOC_BYTES"
    echo "max_stack_bytes=$MAX_STACK_BYTES"
    echo "elf_sha256_a=$ELF_SHA_A"
    echo "elf_sha256_b=$ELF_SHA_B"
    echo 'reproducible_bit_for_bit=true'
    echo 'frame_pointer=OMITTED'
    echo 'needed=NONE'
    echo 'interp=NONE'
    echo 'undefined=NONE'
    echo 'runtime_relocations=NONE'
    echo 'wx_load_segment=NONE'
    echo 'executable_stack=NONE'
    echo 'forbidden_runtime_sections=NONE'
    echo 'gate=PASS'
    echo
    "$READELF_BIN" -h "$FINAL_ELF"
    echo
    "$READELF_BIN" -lW "$FINAL_ELF"
    echo
    "$READELF_BIN" -SW "$FINAL_ELF"
    echo
    "$NM_BIN" -n "$FINAL_ELF"
} | tee "$RECEIPT"

cp "$STACK_FILE" "$OUT/stack-usage.txt"

printf 'PASS: %s %s alloc=%sB stack=%sB sha256=%s\n' \
    "$ARCH_NAME" "$TARGET" "$ALLOC_BYTES" "$MAX_STACK_BYTES" "$ELF_SHA_A"
