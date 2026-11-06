# Mixed / bundled third-party components — do not auto-relicense

`LICENSE_CLEARANCE=TOKEN_VAZIO_COMPONENT_CENSUS`. This is a source-and-obligation routing document, not a license.

GitHub Actions (service) ≠ `gradle/actions` (upstream source) ≠ this fork's local contributions ≠ external hosted actions ≠ compiled `dist/` bundles. Components from different authors may coexist under different notices and licensing conditions. An action runner using `uses: actions/checkout@...` depends on GitHub-hosted software that cannot be rebranded as an authored freestanding binary.

Keep original Gradle Inc. MIT notice under `LICENSE`, and inspect exact version/vendor notices for `dist/`, `sources/`, `.github/`, `android/` and other mixed paths. Do not claim MIT alone exhausts third-party bundled obligations.

Do not classify all `.github/` as authorial; do not classify every `android/` file as independent. Example: `freestanding/atlas_drive_l0/atlas.c` and `android/atlas_wizard/native/atlas.c` are identical observed Git blobs, so there is one shared source lineage.

`claim_allowed=false`, `release_allowed=false`; file-level review and holder evidence are required before changing distribution terms.
