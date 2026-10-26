# RAFCODE evidence receipt (local contribution)

This independent local composite Action is for **hosted GitHub CI**, not the freestanding L0 source or Android runtime. The enclosing GitHub repository is an inherited fork of `gradle/actions`; retain its license/NOTICE and credit. The new code's rights and release status require file-level human review; do not claim ownership of upstream bundles.

## Composition and contract

Pin the reviewed full **commit SHA**, never use a mutable `@main`/`@master`/`@v1`.

```yaml
- uses: rafaelmeloreisnovo/actions/rafcode/evidence-receipt@REVIEWED_40_HEX_SHA
  with:
    expected-source-sha: ${{ github.event.pull_request.head.sha || github.sha }}
    artifact-path: README.md
    falsifier-script: .github/rafcode/verify-readme.sh
    falsifier-id: README_PROVENANCE_NEGATIVES
```

The falsifier script must be reviewed source at the exact tested HEAD, nonempty regular file inside the checkout. It is run by `bash` in a **minimal environment without GitHub tokens or other runner secret variables**. It must exit nonzero on the known-bad control case and zero only when its specified property holds. The receipt action hashes real artifact bytes and the script and checks clean tracked state before/after the test.

The receipt binds `source_commit_sha + GITHUB_RUN_ID + GITHUB_RUN_ATTEMPT + artifact_sha256 + falsifier_id + falsifier_script_sha256 + falsifier_exit_code` and prints canonical JSON and receipt SHA256, including in GitHub Job Summary. It intentionally leaves `github_run_conclusion=NOT_YET_ATTESTED`, `independent_review=NOT_RUN`, `claim_allowed=false`, `promotion=HOLD`. A later independent verifier must inspect the completed GitHub run/job provider evidence and validate artifact hashes and provenance before any production or scientific claim.

## Limits and falsifiers

Run metadata comes from runner environment, not signed GitHub attestation; job/run can still fail after this action. A SHA-256 digest proves local byte identity only, not execution on a physical device, original authorship, source-truth or scientific reproducibility. A shell script can lie or be malicious; source review, independent negative controls, exact HEAD, protected branches, licensed rights and external reviewer remain separate gates. Test fixture only: `python3 rafcode/evidence-receipt/test_receipt.py`. No external package install required (system Bash/Git/Python3 provided by hosted runner).

**Security:** denies path traversal, parent symlinks, absent/empty/oversized files, invalid IDs, mismatched SHA, dirty tracked files, failed falsifiers and output mutation. SHA1 may appear in Git object internals; **do not use Git SHA1 as modern cryptographic authentication**. No release/promotion implied. Never delete upstream and retain a scoped rollback path.
