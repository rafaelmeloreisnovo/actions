#!/usr/bin/env bash
# Local RAFAELIA CI adapter. Upstream licensing remains unchanged.
set -euo pipefail

fail() { printf 'SOURCE_GATE=BLOCKED reason=%s\n' "$1" >&2; exit 1; }
[[ ${RAF_EXPECTED_SHA:-} =~ ^[0-9a-f]{40}$ ]] || fail invalid_expected_sha
actual=$(git rev-parse --verify HEAD) || fail missing_git_head
[[ "$actual" == "$RAF_EXPECTED_SHA" ]] || fail source_sha_mismatch
git diff --quiet --ignore-submodules=none -- || fail modified_worktree
git diff --cached --quiet --ignore-submodules=none -- || fail modified_index

# Untracked, non-ignored files could be consumed by a later compiler invocation.
# core.quotePath=true ensures unusual names (including newlines) remain observable.
untracked=$(git -c core.quotePath=true ls-files --others --exclude-standard) || fail untracked_enumeration
[[ -z "$untracked" ]] || fail untracked_build_input

# Narrow source-root ratchet: ignored files here can alter tested source/CI logic.
# Other ignored build caches remain outside this specific evidence claim.
ignored_critical=$(git -c core.quotePath=true ls-files --others --ignored \
    --exclude-standard -- rafcode/verify-source rafcode/evidence-receipt \
    freestanding/dispatch_l0 governance .github/workflows) || fail ignored_enumeration
[[ -z "$ignored_critical" ]] || fail ignored_critical_input

# This gate covers tracked source at this instant, not later build mutations,
# ignored inputs outside critical roots, signatures, later mutations, runtime or authority.
if [[ -n ${GITHUB_OUTPUT:-} ]]; then
    printf 'source-sha=%s\n' "$actual" >> "$GITHUB_OUTPUT"
fi
printf 'SOURCE_GATE=PASS_SCOPED source_sha=%s claim_allowed=false\n' "$actual"
