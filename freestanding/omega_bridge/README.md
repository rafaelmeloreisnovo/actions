# RAFAELIA Ω — isolated freestanding numerical bridge (DRAFT/HOLD)

## File-level origin and scientific boundaries

- This path is a new RAFAELIA local contribution, imported from the user-supplied `RAFAELIA_OMEGA_freestanding_lab.zip` with SHA-256 `8b2dc23547c21db12bdc020f5545d6b52f10d158fa767f25df4d1ecca7000b47`.
- `omega_core.h` and `test_core.c` are exact local-source copies; `omega_entry.c`, `test_contract.c`, `ci_gate.sh`, this README and the scoped workflow are new changes generated for this proposal. These boundaries do not determine legal ownership; separate license-holder attestation remains pending.
- This is a generic diagonal **weighted residual** in Q16: NOT a cosmological likelihood, NOT a measured physical phenomenon, and NOT an inverse-covariance likelihood.
- Actual RLL covariance matrices/data vectors and sensor calibration are not copied here. `TOKEN_VAZIO` means unavailable, not zero.
- Reference math `rafaelmeloreisnovo/math` reproduces OpenAI-origin manuscripts; they are external comparison material, **not authored RAFAELIA proofs**.
- GitHub Actions hosted infrastructure, `actions/checkout` and `actions/upload-artifact` are separate external tooling, not code authored by RAFAELIA. Inherited `gradle/actions` is not modified.
- Supported builds: freestanding object x86_64/ARMv7/AArch64, no undefined symbols; host ASan/UBSan test runner, no Android APK, no physical ARM execution.

## Run

```sh
bash freestanding/omega_bridge/ci_gate.sh
```

The workflow checks the **exact PR HEAD**, creates an immutable job log and a scoped receipt artifact. Compare its receipt with the historical state, but never overwrite prior receipts. Regressions or unobserved CI mean `HOLD`; no merge, release or scientific claim.

## Seven typed directions (hypothesis graph only)

1. direct/source-to-data; 2. inverse/result-to-source; 3. derivative/transformation;
4. antiderivative/possible-reconstruction; 5. recursive/test-feedback;
6. orthogonal/negative-control; 7. integrative/validated-synthesis.

No direction establishes causality or physical equivalence without independent data and falsifiers.

R3=<F_ok: bounded generic source, F_gap: RLL covariances, sensor calibration, physical ABI, attestation, F_next: exact-HEAD hosted CI then review>.
