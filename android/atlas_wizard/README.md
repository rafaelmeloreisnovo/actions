# RAFAELIA Atlas Wizard · Android APK source candidate

This is a **real Android application source**, separate from PR #21's core-only scope. It runs on Android 10/14 through a Java/ART Activity, direct JNI and freestanding ARMv7 + AArch64 ELF shared libraries. No Gradle project, third-party app library, Google SDK, Internet permission, in-app OAuth/PAT or automatic publication is required.

User flow: open the Wizard; choose up to 16 files with Android Storage Access Framework (ACTION_OPEN_DOCUMENT); SHA-256 only if a readable file is <=8 MiB; then use ACTION_CREATE_DOCUMENT to save an explicit metadata JSON to the Android DocumentsProvider selected by the user. Google Drive may appear if signed in and its DocumentsProvider supports creation. No automatic full-Drive crawl, login, sync or cloud receipt has been implemented.

The C11 planner is compiled from the same source as `freestanding/atlas_drive_l0`, copied under `native/` to make the build narrowly reproducible. It is invoked by JNI on each record, and intentionally reports HOLD when rights/provenance remain unknown. No source bytes are uploaded by the app except the explicit JSON the user saves.

Build on Ubuntu 24.04 with Android SDK 35, Build-tools 35 and a preinstalled Android NDK:
```sh
bash android/atlas_wizard/ci/build_apk.sh
```
Output `android/atlas_wizard/out/RAFAELIA-Atlas-Wizard-arm32-arm64-debug.apk`. A fresh ephemeral **debug signing key** is generated for each test CI build. The signing key is never packaged or uploaded; upgrades between differently signed debug builds may require uninstall.

**Gate:** a hosted signed APK is not a physical Android install test; source, runtime, hardware, remote Drive write and provider availability remain separate. Local metadata hashing runs on the UI thread for bounded files; performance / ANR should be device-tested and improved before larger corpus scans. Always preserve third-party attribution and separate local-source rights review.
