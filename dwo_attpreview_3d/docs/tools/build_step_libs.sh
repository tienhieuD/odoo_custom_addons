#!/bin/sh
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
# Rebuild static/lib/occt and static/lib/rhino3dm from the npm packages (needs node and npm).
# Usage: sh build_step_libs.sh [occt-import-js version] [rhino3dm version]   (default 0.0.23 and 8.35.0)
set -e
T=$(mktemp -d); cd "$T"
echo '{"name":"b","version":"1.0.0","private":true}' > package.json
npm install --silent "occt-import-js@${1:-0.0.23}" "rhino3dm@${2:-8.35.0}" esbuild
OUT="$(dirname "$0")/../../static/lib"
echo 'export { default as occtimportjs } from "occt-import-js";' > entry.js
npx esbuild entry.js --bundle --format=esm --platform=browser --minify --legal-comments=none \
    --external:fs --external:path --external:crypto --external:ws --outfile="$OUT/occt/occt-import-js.bundle.js"
cp node_modules/occt-import-js/dist/occt-import-js.wasm "$OUT/occt/"
cp node_modules/rhino3dm/rhino3dm.module.min.js node_modules/rhino3dm/rhino3dm.wasm "$OUT/rhino3dm/"
echo "built the STEP and 3DM libraries in $OUT"
