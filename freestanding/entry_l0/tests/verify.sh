#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${CC:=clang}"
: "${NM:=nm}"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT HUP INT TERM
"$CC" -std=c11 -O2 -ffreestanding -fno-builtin -Wall -Wextra -Werror -c entry.c -o "$OUT/entry.o"
if "$NM" -u "$OUT/entry.o" | grep -v '^$' >/dev/null; then
    echo "ENTRY_L0_FAIL_UNDEFINED_EXTERNAL" >&2; exit 1
fi
"$CC" -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
    -fno-omit-frame-pointer entry.c tests/test_entry.c -o "$OUT/host_test"
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 "$OUT/host_test"
for TRIPLE in armv7a-linux-gnueabihf aarch64-linux-gnu; do
    "$CC" -std=c11 -O2 -ffreestanding -fno-builtin -Wall -Wextra -Werror \
        -target "$TRIPLE" -c entry.c -o "$OUT/$TRIPLE.o"
    if "$NM" -u "$OUT/$TRIPLE.o" | grep -v '^$' >/dev/null; then
        echo "ENTRY_L0_FAIL_UNDEFINED_EXTERNAL $TRIPLE" >&2; exit 1
    fi
done
printf 'ENTRY_L0_HOST_SCOPE_PASS\nHOST_SANITIZER_PASS\nARMV7_AARCH64_OBJECTS_PASS\nDEVICE_EXECUTION_NOT_RUN\nGRADLE_RUNTIME_NOT_LINKED\nCLAIM_ALLOWED_FALSE\n'
