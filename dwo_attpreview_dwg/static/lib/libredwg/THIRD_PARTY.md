# Third-party code in static/lib/libredwg

| Package | Version | License |
|---|---|---|
| @mlightcad/libredwg-web (JavaScript wrapper, `dist/`) | 0.9.0 | GPL-3.0, https://github.com/mlightcad/libredwg-web |
| LibreDWG compiled to WebAssembly (`wasm/`) | 0.14.x, as built in the package above | GPL-3.0+, https://www.gnu.org/software/libredwg/ |

The whole module is licensed GPL-3 for this reason; the corresponding source is at the links above. The module reads a
DWG file into DXF text in the browser, then draws it with dxf-viewer (MPL-2.0, see ../dxf-viewer/THIRD_PARTY.md).
