# LICENSES — separation by authority, not a blanket relicense

This directory is an **append-only routing overlay** for the `rafaelmeloreisnovo/actions` fork. No permission is granted by these Markdown files. They do not cancel any grants already applicable, and they cannot unilaterally revoke an existing license.

| Region | Rights route | State |
| --- | --- | --- |
| Inherited `gradle/actions` source and action metadata | Root [`LICENSE`](../LICENSE) (MIT, Gradle Inc. notice) + per-file notices | Inherited; not RAFAELIA-original |
| `dist/`, `sources/` and other bundled/vendor files | [Mixed and bundled hold](MIXED_AND_BUNDLED_HOLD.md) | Component-by-component notices unresolved |
| Independently added candidate `freestanding/{kernel4,entry_l0,provenance_core,...}` | [RAFAELIA local hold](RAFAELIA_LOCAL_RIGHTS_HOLD.md) | Holder/actual separate grant not yet verified |
| `.github/`, `android/` mixed files | [Mixed and bundled hold](MIXED_AND_BUNDLED_HOLD.md) | Per-file origin classification required |
| Local `atlas.c` reused in Android | [RAFAELIA local hold](RAFAELIA_LOCAL_RIGHTS_HOLD.md) | Same Git blob, not two authorships |

**Do not assume** a newly separated path is automatically a legally distinct copyright work or that the root MIT license ceases to apply. Any prior grants or third-party obligations survive; verify the applicable rights at the file/revision level before making an irreversible licensing assertion.

Machine route: [license scopes](../provenance/license_scopes.v1.json) → [bounded verifier](../provenance/verify_license_scopes_v1.py) → [adversarial tests](../provenance/tests/test_license_scopes_v1.py).

This is not a substitute for rightsholder-approved license text. A future explicit grant must identify the rightsholder, exact eligible paths/revisions, compatible terms, required notices and release gate. `TOKEN_VAZIO != LICENSE_GRANTED`.
