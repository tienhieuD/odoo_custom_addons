# Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Copy the files of three.js used by the viewers into static/lib/three/ and make the imports relative.
Usage: python3 vendor_three.py PATH_TO_UNPACKED_NPM_PACKAGE_three   (npm pack three@0.187.0 && tar xzf three-*.tgz)
The loaders import the bare name 'three'; the sandboxed viewer pages have no import map (the CSP forbids inline
scripts), so each import is rewritten to the relative path of build/three.module.js."""
import os
import re
import shutil
import sys

SRC = sys.argv[1]
DST = os.path.join(os.path.dirname(__file__), "..", "..", "static", "lib", "three")
JSM = "examples/jsm/"
FILES = [
    "build/three.module.js", "build/three.core.js", "LICENSE",
    JSM + "controls/OrbitControls.js",
    JSM + "loaders/STLLoader.js", JSM + "loaders/OBJLoader.js", JSM + "loaders/GLTFLoader.js",
    JSM + "loaders/3MFLoader.js", JSM + "loaders/PLYLoader.js", JSM + "loaders/FBXLoader.js",
    JSM + "loaders/ColladaLoader.js", JSM + "loaders/TGALoader.js",
    JSM + "loaders/collada/ColladaComposer.js", JSM + "loaders/collada/ColladaParser.js",
    JSM + "utils/BufferGeometryUtils.js", JSM + "utils/SkeletonUtils.js",
    JSM + "curves/NURBSCurve.js", JSM + "curves/NURBSUtils.js",
    JSM + "libs/fflate.module.js",
]
shutil.rmtree(DST, ignore_errors=True)
for rel in FILES:
    out = os.path.join(DST, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    text = open(os.path.join(SRC, rel), encoding="utf-8").read()
    if rel.endswith(".js") and rel.startswith(JSM):
        up = os.path.relpath(os.path.join(DST, "build/three.module.js"), os.path.dirname(out)).replace(os.sep, "/")
        text = re.sub(r"""from\s+(['"])three\1""", lambda m: "from '%s'" % up, text)
    open(out, "w", encoding="utf-8").write(text)
print("copied", len(FILES), "files")
