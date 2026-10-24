#!/bin/sh
# HOST ONLY. Does not change the checked-out repository or run embedded targets.
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
HOST_CC=${HOST_CC:-clang}
CROSS_CC=${CROSS_CC:-clang}
command -v "$HOST_CC" >/dev/null 2>&1 || exit 2
command -v "$CROSS_CC" >/dev/null 2>&1 || exit 2
command -v nm >/dev/null 2>&1 || exit 2
for level in 0 2; do
  "$HOST_CC" -std=c11 -O"$level" -Wall -Wextra -Werror -fsanitize=address,undefined \
    "$BASE/dispatch.c" "$BASE/tests/test_dispatch.c" -o "$TMP/test$level"
  "$TMP/test$level"
done
for item in x86_64-unknown-none-elf armv7-none-eabi aarch64-none-elf; do
  "$CROSS_CC" --target="$item" -std=c11 -Os -Wall -Wextra -Werror \
    -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-pie \
    -fno-unwind-tables -fno-asynchronous-unwind-tables -c "$BASE/dispatch.c" -o "$TMP/$item-a.o"
  "$CROSS_CC" --target="$item" -std=c11 -Os -Wall -Wextra -Werror \
    -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-pie \
    -fno-unwind-tables -fno-asynchronous-unwind-tables -c "$BASE/dispatch.c" -o "$TMP/$item-b.o"
  test -z "$(nm -u "$TMP/$item-a.o")"
  cmp -s "$TMP/$item-a.o" "$TMP/$item-b.o"
  printf '%s %s\n' "$item" "$(sha256sum "$TMP/$item-a.o" | cut -d ' ' -f1)"
done
printf '%s\n' 'LOCAL_DISPATCH_L0_PASS_SCOPED: hosted 2 optimization+sanitizer modes; 3 freestanding object targets'
