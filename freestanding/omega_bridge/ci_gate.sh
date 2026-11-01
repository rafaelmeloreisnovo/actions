#!/usr/bin/env bash
# Authored isolated gate: no inherited Gradle Actions code executed by this gate.
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${EXPECTED_SOURCE_SHA:=LOCAL_UNPINNED}"
if [[ "$EXPECTED_SOURCE_SHA" != LOCAL_UNPINNED ]]; then
  actual=$(git rev-parse HEAD)
  [[ "$actual" == "$EXPECTED_SOURCE_SHA" ]] || { echo "FAIL_EXACT_HEAD actual=$actual expected=$EXPECTED_SOURCE_SHA"; exit 10; }
fi
DIR=freestanding/omega_bridge
OUT="${RUNNER_TEMP:-/tmp}/rafaelia_omega_bridge_gate"
mkdir -p "$OUT"
for test in test_core test_contract; do
 clang -std=c11 -O1 -g -ffreestanding -fno-builtin -Wall -Wextra -Werror \
   -fsanitize=address,undefined -fno-omit-frame-pointer "$DIR/$test.c" -o "$OUT/$test"
 ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 "$OUT/$test"
done
for spec in 'x86_64 x86_64-unknown-none-elf -mno-red-zone' \
            'armv7 armv7-none-eabi -march=armv7-a' \
            'aarch64 aarch64-none-elf -march=armv8-a'; do
  read -r arch triple flags <<< "$spec"
  clang --target="$triple" "$flags" -std=c11 -O2 -ffreestanding -fno-builtin \
    -fno-stack-protector -Wall -Wextra -Werror \
    -c "$DIR/omega_entry.c" -o "$OUT/$arch.o"
  test -z "$(nm -u "$OUT/$arch.o")" || { echo "UNDEFINED_SYMBOL=$arch"; exit 11; }
  echo "ARCH_OBJECT=$arch PASS scope=OBJECT_ONLY"
done
printf 'expected_source_sha=%s\norigin=RAFAELIA_LOCAL_LAB\nscope=HOST_SANITIZER_AND_OBJECT_ONLY\ncalibrated_rll_covariance=TOKEN_VAZIO\nsensor_calibration=TOKEN_VAZIO\nphysical_arm32_arm64=NOT_RUN\nclaim_allowed=false\n' "$EXPECTED_SOURCE_SHA" | tee "$OUT/receipt.txt"
sha256sum "$DIR/omega_core.h" "$DIR/omega_entry.c" "$DIR/test_core.c" "$DIR/test_contract.c" | tee -a "$OUT/receipt.txt"
echo 'GATE_PASS_SCOPE_ONLY'
