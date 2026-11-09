# Kernel4 output-path safety hotfix — 2026-11-09

PRODUCER: rafaelmeloreisnovo/actions, local independently-authored Kernel4 lane.
UPSTREAM_BOUNDARY: inherited Gradle/Node setup-gradle implementation is unchanged and retains license/credits; this shell guard is hosted CI only.
SOURCE: main@6eb18b9366011d20d1687efbc51135ecaa7f9ab0; exact prior file blobs ci_gate.sh ffafa7dc40307b8b0e3d0d0ccef1e2de691c8a1e, workflow c568d5db418c4e096eb0bd02a692b4cf692f423b.
RISK: `ci_gate.sh` deletes user-specified `OUT` via `rm -rf` without restricting the path.
CHANGE: refuse anything outside `out/kernel4/<single safe basename>`; refuse path separators, traversal, dots, absolute paths and symlinks at out, out/kernel4 and the destination; validate before resolving tools, before removal.
FALSIFIER: nine intentionally unsafe paths (including symlink destination and parent) must all be refused without removing an unrelated sentinel file. Existing x86_64/ARMv7/AArch64 link/ELF/stack-size/reproducibility CI must still pass at exact head.
SCOPE: protects CI accidental unsafe OUT usage; assumes no hostile concurrent filesystem race in runner. An absolute zero-risk deletion primitive is not claimed.
OUTPUT: shell remains hosted; linked C11 Kernel4 remains freestanding. Actions YAML itself runs on GitHub provider; no claim of full product freestanding.
AUTHORITY: user requested surgical safety hotfix. No unrelated code, no active release or auto-merge.
EVIDENCE: local hosted guard negative tests 9/9 PASS; GitHub Actions exact-head CI PENDING until readback.
ROLLBACK: close draft PR without merge; if reviewed/merged, revert only scoped guard/test/workflow; preserve prior evidence as predecessor.
CLAIM_ALLOWED=false for physical hardware/performance/entire Gradle Actions dependency freedom.
