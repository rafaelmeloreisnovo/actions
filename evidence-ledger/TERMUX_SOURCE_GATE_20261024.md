# Termux source identity — local validation receipt

Base/rollback: `8dd8e164b6cb01fc79e0811c6eb091d512f5382a`.
Authority: user-authorized draft hotfix in the actions producer; public source only.
Classification: governance=DRAFT_NO_PROMOTION; data=PUBLIC_SOURCE;
privacy=NO_DEVICE_OR_SECRET_DATA; security=FAIL_CLOSED_SOURCE_IDENTITY.

Delta: isolated hosted Bash/Git action; eight integration tests against real temporary
Git repositories, including malformed/injected SHA, wrong HEAD, staged/unstaged
changes, deletion and missing repository. Local result: 8/8 PASS; Bash syntax PASS.
Python stdlib is test-only. Bash/Git are explicit existing CI dependencies.
No change to upstream Gradle implementation, existing freestanding cores or licenses.

Consumer route: termux-packages prefix gate and termux-app-rafacodephi beta contract.
Federated Mapa route: TOKEN_VAZIO (not invented; no federated state promotion).
CI at candidate SHA: NOT_YET_OBSERVED. Android/APK/pkg/physical ARM: NOT_RUN.
Revert this scoped commit or retain prior consumer pin; no branch/history deletion.
F_ok=local falsifiers PASS; F_gap=remote replay and human review;
F_next=pin consumer drafts to this commit and verify their exact-head runs.
claim_allowed=false; release_allowed=false.
