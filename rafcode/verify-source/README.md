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

## P0 scoped source-input ratchet (2026-10-26; HOLD candidate)

Predecessor: tracked HEAD/index check; older HOLD branch additionally blocked ordinary untracked files. This separately versioned candidate also blocks **ignored files** within `rafcode/verify-source`, `rafcode/evidence-receipt`, `freestanding/dispatch_l0`, `governance`, and `.github/workflows`. These roots contain source, policy, or CI logic. Ignored build output **outside** those roots remains outside the guarantee to avoid mass-breaking inherited Gradle workflows. Passing the gate does not prove toolchain attestation, immutable post-gate inputs, authentic author/license, hardware runtime, or provider branch protection.

The new hosted workflow `.github/workflows/ci-rafcode-source-gate.yml` is scoped to gate/workflow changes, uses only Git/Bash/Python provided by the runner, validates exact HEAD before and after 14 host-only tests, and does not authorize merges. Results remain `PROVIDER_NOT_OBSERVED` until a run ID, jobs and steps bound to the exact candidate commit are independently retrieved. Authorial origin and rights for new deltas require human adjudication; the Gradle fork notices remain intact.

**Acceptance:** clean checkout and unrelated ignored cache allowed; modified tracked, staged, non-ignored untracked, and critical ignored files denied, with all old tests intact. **Rollback:** leave this HOLD branch unmerged, retaining source history. `claim_allowed=false`, `PROMOTION=HOLD`.
