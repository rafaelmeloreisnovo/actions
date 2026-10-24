#!/usr/bin/env bash
# Local RAFAELIA CI adapter. Upstream licensing remains unchanged.
set -euo pipefail

fail() { printf 'SOURCE_GATE=BLOCKED reason=%s\n' "$1" >&2; exit 1; }
[[ ${RAF_EXPECTED_SHA:-} =~ ^[0-9a-f]{40}$ ]] || fail invalid_expected_sha
actual=$(git rev-parse --verify HEAD) || fail missing_git_head
[[ "$actual" == "$RAF_EXPECTED_SHA" ]] || fail source_sha_mismatch
git diff --quiet --ignore-submodules=none -- || fail modified_worktree
git diff --cached --quiet --ignore-submodules=none -- || fail modified_index

# This gate covers tracked source at this instant, not later build mutations,
# ignored/untracked files, signatures, test results, runtime or authorization.
if [[ -n ${GITHUB_OUTPUT:-} ]]; then
    printf 'source-sha=%s\n' "$actual" >> "$GITHUB_OUTPUT"
fi
printf 'SOURCE_GATE=PASS_SCOPED source_sha=%s claim_allowed=false\n' "$actual"
