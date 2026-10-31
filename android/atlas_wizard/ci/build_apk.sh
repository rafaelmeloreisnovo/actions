#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
OUT="$ROOT/out"
mkdir -p "$OUT/classes" "$OUT/dex" "$OUT/so/armeabi-v7a" "$OUT/so/arm64-v8a"
PLATFORM="$SDK/platforms/android-35/android.jar"
BUILD="$SDK/build-tools/35.0.0"
NDK="${ANDROID_NDK_HOME:-${ANDROID_NDK_ROOT:-${ANDROID_NDK:-}}}"
if [[ -z "$NDK" ]]; then
 mapfile -t ndks < <(find "$SDK/ndk" -mindepth 1 -maxdepth 1 -type d | sort -V)
 NDK="${ndks[0]:-}"
fi
CC="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin"
for f in "$PLATFORM" "$BUILD/aapt2" "$BUILD/d8" "$BUILD/zipalign" "$BUILD/apksigner" "$CC/clang";do
 test -e "$f" || { echo "TOOLCHAIN_UNAVAILABLE: $f" >&2;exit 20; }
done
javac -source 8 -target 8 -Xlint:-options -encoding UTF-8 \
 -classpath "$PLATFORM" -d "$OUT/classes" \
 "$ROOT/src/org/rafaelia/atlas/AtlasWizard.java"
mapfile -t classes < <(find "$OUT/classes" -type f -name '*.class' | sort)
"$BUILD/d8" --min-api 23 --lib "$PLATFORM" --output "$OUT/dex" "${classes[@]}"
for pair in 'armeabi-v7a:armv7a-linux-androideabi23' 'arm64-v8a:aarch64-linux-android23';do
 IFS=: read -r abi target <<< "$pair"
 "$CC/clang" --target="$target" -std=c11 -O2 -fPIC \
  -ffreestanding -fno-builtin -fno-stack-protector -Wall -Wextra -Werror \
  -fno-unwind-tables -fno-asynchronous-unwind-tables \
  -shared -nostdlib -Wl,--no-undefined -Wl,-soname,libatlas_l0.so \
  -I "$ROOT/native" "$ROOT/native/atlas.c" "$ROOT/native/jni_atlas.c" \
  -o "$OUT/so/$abi/libatlas_l0.so"
 if "$CC/llvm-nm" -u "$OUT/so/$abi/libatlas_l0.so" | grep -q .;then
   echo "FAILED_NATIVE_UNDEFINED_SYMBOLS $abi" >&2;exit 21
 fi
 "$CC/llvm-readelf" -h "$OUT/so/$abi/libatlas_l0.so" | grep -E 'Class:|Machine:'
done
"$BUILD/aapt2" link -I "$PLATFORM" --manifest "$ROOT/AndroidManifest.xml" \
 --min-sdk-version 23 --target-sdk-version 28 \
 --version-code 1 --version-name 0.1.0 -o "$OUT/unsigned.apk"
(cd "$OUT/dex" && zip -q "$OUT/unsigned.apk" classes.dex)
mkdir -p "$OUT/apklibs/lib/armeabi-v7a" "$OUT/apklibs/lib/arm64-v8a"
cp "$OUT/so/armeabi-v7a/libatlas_l0.so" "$OUT/apklibs/lib/armeabi-v7a/"
cp "$OUT/so/arm64-v8a/libatlas_l0.so" "$OUT/apklibs/lib/arm64-v8a/"
(cd "$OUT/apklibs" && zip -qr "$OUT/unsigned.apk" lib)
"$BUILD/zipalign" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
keytool -genkeypair -noprompt -keystore "$OUT/debug.jks" \
 -storepass 'test-key-not-production' -keypass 'test-key-not-production' \
 -alias atlas-debug -keyalg RSA -keysize 2048 -validity 30 \
 -dname 'CN=RAFAELIA Ephemeral Test' >/dev/null 2>&1
APK="$OUT/RAFAELIA-Atlas-Wizard-arm32-arm64-debug.apk"
"$BUILD/apksigner" sign --ks "$OUT/debug.jks" --ks-key-alias atlas-debug \
 --ks-pass pass:test-key-not-production --key-pass pass:test-key-not-production \
 --out "$APK" "$OUT/aligned.apk"
"$BUILD/apksigner" verify --verbose "$APK"
"$BUILD/zipalign" -c 4 "$APK"
python3 - "$APK" <<'PY'
import sys,zipfile,os,hashlib,json
path=sys.argv[1]
with zipfile.ZipFile(path) as z:
    names=set(z.namelist())
    needed={'AndroidManifest.xml','classes.dex','lib/armeabi-v7a/libatlas_l0.so','lib/arm64-v8a/libatlas_l0.so'}
    assert needed <= names, needed-names
    assert z.testzip() is None
    receipt={'status':'SIGNED_DEBUG_APK_STRUCTURALLY_VERIFIED',
       'bytes':os.path.getsize(path),'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),
       'entries':sorted(names),'device_install':'NOT_RUN','drive_provider_readback':'NOT_RUN','claim_allowed':False}
    with open(path+'.receipt.json','w') as out:json.dump(receipt,out,indent=2)
    print(json.dumps(receipt,indent=2))
PY
