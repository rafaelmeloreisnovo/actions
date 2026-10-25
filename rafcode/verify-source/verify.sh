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

# An ignored file can still be consumed by a build through include paths,
# globs or implicit tool discovery. On a fresh checkout, fail closed on any
# ignored build input; never mistake .gitignore for a security boundary.
ignored=$(git -c core.quotePath=true ls-files --others --ignored --exclude-standard) || fail ignored_enumeration
[[ -z "$ignored" ]] || fail ignored_build_input

# This gate proves only the clean pre-build checkout at this instant.
# Later build mutations, signatures, test results and runtime are not covered.
if [[ -n ${GITHUB_OUTPUT:-} ]]; then
    printf 'source-sha=%s\n' "$actual" >> "$GITHUB_OUTPUT"
fi
printf 'SOURCE_GATE=PASS_SCOPED source_sha=%s claim_allowed=false\n' "$actual"
