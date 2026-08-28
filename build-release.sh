#!/usr/bin/env bash
set -euo pipefail

cd frontend && npm run tauri build -- --no-bundle && cd ..

OUT="release/rota-automation"
rm -rf "$OUT"
mkdir -p "$OUT/backend/utils" "$OUT/data"

cp frontend/src-tauri/target/release/rota-automation-frontend.exe "$OUT/"
cp backend/main.py backend/constants.py backend/requirements.txt "$OUT/backend/"
cp backend/utils/*.py "$OUT/backend/utils/"

cd release && powershell -Command "Compress-Archive -Path 'rota-automation/*' -DestinationPath 'rota-automation.zip' -Force"
echo "Release artifact: release/rota-automation.zip"
