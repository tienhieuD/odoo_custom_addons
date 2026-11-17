#!/bin/sh
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
# Rebuild static/lib/dxf-viewer/dxf-viewer.bundle.js (needs node and npm).
# Usage: sh build_dxf_viewer.sh [version]   (default 1.0.51)
set -e
V=${1:-1.0.51}
T=$(mktemp -d); cd "$T"
echo '{"name":"b","version":"1.0.0","private":true}' > package.json
npm install --silent "dxf-viewer@$V" esbuild @fontsource/noto-sans
echo 'export { DxfViewer } from "dxf-viewer";' > entry.js
# dxf-viewer imports two files of three by their deep path; both are exported by the main package, so alias them
mkdir shims
echo 'export { ShapePath } from "three";' > shims/ShapePath.js
echo 'export { ShapeUtils } from "three";' > shims/ShapeUtils.js
npx esbuild entry.js --bundle --format=esm --minify --external:three \
    --alias:three/src/extras/core/ShapePath.js=./shims/ShapePath.js --alias:three/src/extras/ShapeUtils.js=./shims/ShapeUtils.js \
    --legal-comments=none --outfile=bundle.js
OUT="$(dirname "$0")/../../static/lib/dxf-viewer"
sed 's#from"three"#from"/dwo_attpreview_webgl/asset/lib/three/build/three.module.js"#g' bundle.js > "$OUT/dxf-viewer.bundle.js"
cp node_modules/dxf-viewer/LICENSE "$OUT/LICENSE-dxf-viewer-MPL-2.0.txt"
for f in latin latin-ext vietnamese; do cp node_modules/@fontsource/noto-sans/files/noto-sans-$f-400-normal.woff "$OUT/fonts/"; done
echo "built dxf-viewer $V in $OUT"
