# Exact source gate — hosted CI adapter

Use `rafaelmeloreisnovo/actions/rafcode/verify-source@<reviewed-full-SHA>`
immediately after checkout and before source transformations. Set checkout `ref`
and `expected-sha` to `${{ github.event.pull_request.head.sha || github.sha }}`.
Keep `persist-credentials: false` and `permissions: contents: read` in callers.

The gate rejects malformed SHA, wrong HEAD, changed tracked files and changed
index; it emits `source-sha` only after success. It does not checkout code,
download tools, execute supplied commands, publish or authorize a merge.

Dependencies: runner-provided Bash and Git, build/CI only. This is a hosted
adapter, not freestanding code. No Node or new external action is introduced.
Ignored/untracked files and subsequent changes are outside this gate; callers
must control build inputs and bind resulting artifact digests separately.
Git commit equality is not signature authenticity or runtime proof.

Test: `python3 rafcode/verify-source/test_verify.py` (Python stdlib, host only).
Local delta; inherited Gradle implementation and notices remain unchanged.
No new license grant is asserted. Rollback: retain previous consumer pin and
revert the scoped consumer commit. `claim_allowed=false`.
