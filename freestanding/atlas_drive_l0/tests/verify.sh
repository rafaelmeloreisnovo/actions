#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
cd "$ROOT"
: "${HOST_CC:=clang}"
: "${CROSS_CC:=clang}"
for opt in 0 2; do
  "$HOST_CC" -std=c11 -O"$opt" -Wall -Wextra -Werror \
    -fno-builtin -fno-stack-protector \
    freestanding/atlas_drive_l0/atlas.c \
    freestanding/atlas_drive_l0/tests/test_atlas.c -o "$TMP/test_$opt"
  "$TMP/test_$opt"
  printf 'HOST_O%s PASS\n' "$opt"
done
for item in 'x86_64-unknown-none-elf' 'armv7-none-eabi' 'aarch64-none-elf'; do
  "$CROSS_CC" --target="$item" -std=c11 -O2 -Wall -Wextra -Werror \
    -ffreestanding -fno-builtin -fno-stack-protector \
    -fno-unwind-tables -fno-asynchronous-unwind-tables \
    -c freestanding/atlas_drive_l0/atlas.c -o "$TMP/${item}.o"
  if nm -u "$TMP/${item}.o" | grep .; then echo 'UNDEFINED_SYMBOLS' >&2; exit 1; fi
  printf 'OBJECT_%s ZERO_UNDEFINED PASS\n' "$item"
done
printf 'ATLAS_L0_HOST_SCOPE_PASS: no APK, Drive, TLS, ARM device or GPU execution\n'
