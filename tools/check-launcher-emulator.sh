#!/usr/bin/env bash
set -euo pipefail
APK="${1:?Pass built APK}"
API="${2:?Pass emulator API level}"
test -s "$APK" || { echo "APK file missing"; exit 1; }
REPORTED="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
test "$REPORTED" = "$API" || { echo "Wrong emulator API: expected $API, got $REPORTED"; exit 1; }
adb install -r "$APK"
adb logcat -b crash -c || true
adb shell am start -W -n app.orchard.tv/.MainActivity
sleep 12
PID="$(adb shell pidof app.orchard.tv | tr -d '\r' || true)"
if [[ -z "$PID" ]]; then
  echo "Aerial Launcher process exited on API $API"
  adb logcat -b crash -d
  exit 1
fi
# Do not change HOME defaults or grant special permissions.
adb shell input keyevent KEYCODE_DPAD_DOWN
adb shell input keyevent KEYCODE_DPAD_UP
adb shell input keyevent KEYCODE_DPAD_RIGHT
adb shell input keyevent KEYCODE_BACK
sleep 2
adb logcat -b crash -d > aerial-emulator-crash.txt || true
if grep -Fq "Process: app.orchard.tv" aerial-emulator-crash.txt; then
  echo "Launcher crash detected"
  cat aerial-emulator-crash.txt
  exit 1
fi
echo "Android API $API launcher launch/remote input smoke check PASSED (emulator, not TV hardware)."
