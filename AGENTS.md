# AGENTS.md — RAFAELIA / actions fork — tooling boundary S13

> Agent instructions on this **isolated branch only**. Preserve the upstream `gradle/actions` authorship, license and behavior. No claim of origin for upstream code.

## Authority and limits
This repository is a **CI/build-tool fork**, not the RAFAELIA freestanding L0 implementation and not the Android runtime owner. Follow the owner's current task instructions, the local workflow/action manifest, and the relevant upstream license. `Mapa` governs federated routes; `RafPolimata` owns the low-level C matrix module; `RafGitTools` owns structural evidence gates; Termux owns Android integration.

An agent **must not silently import** Node, npm, Java, Gradle, Android SDK/NDK, JNI, JIT, libc or native dynamic loaders into a PURE_CORE object. Those dependencies may legitimately exist in a **hosted build action**. Retaining a tool is not claiming that the linked L0 runtime depends on it. Avoid introducing obsolete Node.js 20 as an active build baseline; use supported toolchain versions and pin external actions/references by immutable SHA when available.

## Mandatory preflight
Resolve the exact repository, branch, HEAD, requested goal, affected AGENTS scope, upstream license, existing workflow tests, risk/rollback and required human approval. Distinguish:
- BUILD_TOOLING: Node/Java/Gradle/NDK/SDK, actions runners and network downloads (explicit versions + trust).
- L0_OBJECT: no undefined symbols, libc, heap, JNI, syscalls, platform callbacks (verified by the producer's binary gate).
- ANDROID_RUNTIME: installer, ART/JIT, package signature, ABI, real device/OS logging and permissions (separate owner).
- FEDERATION: counts 18 S6 branches, 28 S7 requests, 13 prefixes × 7 friction lanes, 22 quality criteria (scope inventory only).

## CI evidence
No action workflow by itself proves Android execution, security certification, 342 intellectual origins or the complete 9×51 corpus crosswalk. Record exact-head build receipts. Do not mark an unrun job PASS; do not mock phone success. No automatic merge, no deletion, no branch rewrite, no licensing changes to upstream. Maintain `TOKEN_VAZIO`, `claim_allowed=false`, rollback and human review.

Only this AGENTS file is proposed in S13; no workflow or upstream code is changed by this proposal.
