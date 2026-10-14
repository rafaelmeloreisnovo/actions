#!/usr/bin/env bash
# HOST ADAPTER: never mislabel Android Gradle and SDK as freestanding.
set -euo pipefail
export LC_ALL=C TZ=UTC
[[ $# == 2 ]] || { echo 'Usage: build_debug.sh PROJECT_DIR RELATIVE_APK_PATH' >&2; exit 2; }
PROJECT=$(cd "$1" && pwd -P)
APK_REL=$2
[[ "$APK_REL" != /* && "$APK_REL" != *'..'* ]] || { echo 'unsafe APK path' >&2; exit 2; }
[[ -f "$PROJECT/gradlew" ]] || { echo 'Gradle wrapper missing' >&2; exit 3; }
[[ -f "$PROJECT/settings.gradle" || -f "$PROJECT/settings.gradle.kts" ]] || { echo 'Gradle project missing' >&2; exit 3; }
for tool in java sha256sum zipalign apksigner; do
 command -v "$tool" >/dev/null || { echo "toolchain missing: $tool" >&2; exit 3; }
done
cd "$PROJECT"
bash ./gradlew --offline --no-daemon --console=plain :app:assembleDebug
[[ -f "$APK_REL" && ! -L "$APK_REL" ]] || { echo 'APK not produced' >&2; exit 4; }
zipalign -c -v 4 "$APK_REL" >/dev/null
apksigner verify --verbose "$APK_REL" >/dev/null
printf 'receipt=RAFAELIA_HOST_DEBUG_APK_V1\n'
printf 'scope=HOSTED_EXISTING_ANDROID_TOOLCHAIN_NOT_FREESTANDING_COMPILER\n'
printf 'source_sha=%s\n' "$(git rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)"
printf 'apk_sha256=%s\n' "$(sha256sum "$APK_REL" | cut -d' ' -f1)"
printf 'apk_relative_path=%s\n' "$APK_REL"
printf 'zipalign=VERIFIED\nsigning=VERIFIED_BY_ANDROID_SDK\n'
printf 'release_signing=NOT_RUN\nphysical_execution=NOT_RUN\n'
