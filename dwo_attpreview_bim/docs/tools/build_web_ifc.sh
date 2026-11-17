#!/bin/sh
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
# Rebuild static/lib/web-ifc/ from the npm package (needs node and npm). Usage: sh build_web_ifc.sh [version]
set -e
V=${1:-0.0.79}
T=$(mktemp -d); cd "$T"
echo '{"name":"b","version":"1.0.0","private":true}' > package.json
npm install --silent "web-ifc@$V" esbuild
OUT="$(dirname "$0")/../../static/lib/web-ifc"
npx esbuild node_modules/web-ifc/web-ifc-api.js --minify --format=esm --legal-comments=none --outfile="$OUT/web-ifc-api.js"
cp node_modules/web-ifc/web-ifc.wasm "$OUT/"
cp node_modules/web-ifc/LICENSE.md "$OUT/LICENSE-web-ifc-MPL-2.0.txt"
echo "built web-ifc $V in $OUT"
