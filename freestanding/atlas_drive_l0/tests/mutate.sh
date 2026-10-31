#!/bin/sh
# Independent host-only mutation tests. Mutants MUST be detected by the same test oracle.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
cd "$ROOT"
SOURCE=freestanding/atlas_drive_l0/atlas.c
HEADER=freestanding/atlas_drive_l0
TEST=freestanding/atlas_drive_l0/tests/test_atlas.c
for mode in promote gap duplicate ttl empty; do
 case "$mode" in
 promote) sed 's/out->claim_allowed=0u;/out->claim_allowed=1u;/' "$SOURCE" > "$TMP/$mode.c" ;;
 gap) sed 's/if(p->gap_type!=RA_GAP_NONE)/if(0u)/' "$SOURCE" > "$TMP/$mode.c" ;;
 duplicate) sed 's/if(duplicate){dup|=bit;bad=1u;}/if(duplicate){dup|=bit;}/' "$SOURCE" > "$TMP/$mode.c" ;;
 empty) sed 's/if(count==0u){out->status=RA_MISSING;return;}/if(0u){out->status=RA_MISSING;return;}/' "$SOURCE" > "$TMP/$mode.c" ;;
 ttl) sed 's/if(!req->ttl||req->elapsed>=req->ttl)/if(0u)/' "$SOURCE" > "$TMP/$mode.c" ;;
 esac
 if cmp -s "$SOURCE" "$TMP/$mode.c"; then echo "MUTANT_NOT_APPLIED $mode" >&2; exit 1; fi
 clang -I "$HEADER" -std=c11 -O2 -Wall -Wextra -Werror \
  "$TMP/$mode.c" "$TEST" -o "$TMP/$mode"
 if "$TMP/$mode"; then echo "MUTANT_SURVIVED $mode" >&2; exit 1; fi
 printf 'MUTANT_KILLED %s\n' "$mode"
done
