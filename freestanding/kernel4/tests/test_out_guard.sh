#!/usr/bin/env bash
# Hosted-only negative falsifiers; never linked into Kernel4.
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)/ci_gate.sh"
TMP="$(mktemp -d)"
trap 'rm -rf -- "$TMP"' EXIT
cd "$TMP"
mkdir -p safe
printf 'DO_NOT_ERASE\n' > safe/marker
failures=0
checks=0
reject() {
  local candidate=$1
  local label=$2
  checks=$((checks + 1))
  if bash "$SCRIPT" x86_64 x86_64-unknown-none-elf ELF64 'Advanced Micro Devices X86-64' '' "$candidate" > test.log 2>&1; then
    printf 'FAIL accepted %s: %s\n' "$label" "$candidate" >&2
    failures=$((failures + 1))
  elif ! grep -Fq 'unsafe output path' test.log; then
    printf 'FAIL unrelated reason %s: %s\n' "$label" "$candidate" >&2
    failures=$((failures + 1))
  fi
  if [ ! -f safe/marker ]; then
    printf 'FAIL changed sentinel at %s\n' "$label" >&2
    failures=$((failures + 1))
  fi
}
reject 'safe' 'unrelated-relative'
reject '../safe' 'traversal'
reject "$TMP/safe" 'absolute-path'
reject 'out/kernel4/../safe' 'traversal-inside-prefix'
reject 'out/kernel4/x/../safe' 'nested-prefix'
reject 'out/kernel4/' 'empty-basename'
reject 'out/kernel4/a.b' 'dotted-name'
# Budget must be validated before shell arithmetic or compiler invocation.
for budget in 0 abc '1+2' -1 0002 1234567890; do
  checks=$((checks + 1))
  if MAX_ALLOC_BYTES="$budget" bash "$SCRIPT" x86_64 x86_64-unknown-none-elf ELF64 'Advanced Micro Devices X86-64' '' 'out/kernel4/budget_guard' > test.log 2>&1; then
    printf 'FAIL accepted allocation budget: %s\n' "$budget" >&2
    failures=$((failures + 1))
  elif ! grep -Fq 'invalid allocation budget' test.log; then
    printf 'FAIL wrong budget rejection: %s\n' "$budget" >&2
    failures=$((failures + 1))
  fi
  if [ ! -f safe/marker ]; then
    printf 'FAIL sentinel missing for budget %s\n' "$budget" >&2
    failures=$((failures + 1))
  fi
done
mkdir -p out/kernel4
ln -s "$TMP/safe" out/kernel4/armv7
reject 'out/kernel4/armv7' 'symlink-destination'
rm out/kernel4/armv7
rm -r out
ln -s "$TMP/safe" out
reject 'out/kernel4/armv7' 'symlink-parent'
printf 'KERNEL4_OUT_GUARD negative=%s failures=%s\n' "$checks" "$failures"
test "$checks" -eq 15 && test "$failures" -eq 0
