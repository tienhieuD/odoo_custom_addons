# Third-party code in static/lib

| Folder | Package | Version | License |
|---|---|---|---|
| occt/ | occt-import-js (Open CASCADE Technology compiled to WebAssembly, by kovacsv) | 0.0.23 | LGPL-2.1 (see occt/LICENSE-LGPL-2.1.txt, LICENSE-occt-import-js.txt, LICENSE-opencascade.txt); source: https://github.com/kovacsv/occt-import-js and https://github.com/Open-Cascade-SAS/OCCT |
| rhino3dm/ | rhino3dm (McNeel) | 8.35.0 | MIT (see rhino3dm/LICENSE-rhino3dm-MIT.txt); source: https://github.com/mcneel/rhino3dm |

`occt/occt-import-js.bundle.js` is the unmodified `occt-import-js.js` of the npm package, wrapped as an ES module with
esbuild (`docs/tools/build_step_libs.sh`), and `occt-import-js.wasm` is the unmodified WebAssembly build. Both are
separate files loaded at run time, so the library can be replaced by a newer or modified build (LGPL-2.1). The three.js
files used by the viewer are in the module dwo_attpreview_webgl (MIT).
