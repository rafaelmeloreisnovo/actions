# START HERE · Actions authorial nuclei and license scopes

**Fork:** `rafaelmeloreisnovo/actions`; inherited source authority `gradle/actions`.
**Evidence anchor:** `main@2138f9c78df588a577e560c7ae3dfdb89c5a1be9`.

## Zero-friction routes
1. Existing pure kernels: `freestanding/kernel4/kernel4.c`, `freestanding/entry_l0/entry.c`, `freestanding/provenance_core/rights_core.c`; do not duplicate, rewrite or rename compiled code just to claim ownership.
2. Separate rights destinations: `LICENSE` (upstream MIT, untouched), `LICENSES/RAFAELIA_LOCAL_RIGHTS_HOLD.md` (local candidate, license terms undecided), `LICENSES/MIXED_AND_BUNDLED_HOLD.md` (bundles/workflow/platform).
3. Read source identity `provenance/license_scopes.v1.json` and run `python3 provenance/verify_license_scopes_v1.py` + `python3 -m unittest discover -s provenance/tests -p 'test_*.py'`.
4. Execute existing `.github/workflows/ci-rafaelia-rights.yml` for exact HEAD scoped verification; Actions YAML/runner/Clang/Python are hosted adapters, not freestanding. It tests the pre-existing independent C provenance core.

## Gates
`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. `TOKEN_VAZIO != 0`.
`LOCAL_CANDIDATE != LEGAL_AUTHORSHIP_PROVED`. `HOLD != SEPARATE_LICENSE_GRANTED`. `CI_PASS != PHYSICAL_PASS`.

This overlay is deliberately a *selected-root, eight-blob census*, not legal clearance of the entire fork. Local nuclei have no **new** license granted by this patch. Historic grants are not revoked.

**Rollback:** close draft PR without merge; existing upstream files and root `LICENSE` remain unchanged. A later license decision by the rights holder is a separate reviewed, file-level successor event.

R3=⟨F_ok: scoped authorial routing with negative falsifiers; F_gap: rights holder, license text and full upstream/vendor census; F_next: exact-head test then explicit scoped license decision⟩
