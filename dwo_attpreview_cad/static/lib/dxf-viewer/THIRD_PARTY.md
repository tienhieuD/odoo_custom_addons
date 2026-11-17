# Third-party code in dxf-viewer.bundle.js

Built with esbuild from the npm packages below (`docs/tools/build_dxf_viewer.sh`). The imports of `three` point to
the copy of three.js shipped by `dwo_attpreview_webgl`.

| Package | Version | License |
|---|---|---|
| dxf-viewer (SPH Engineering) | 1.0.51 | MPL-2.0 (see LICENSE-dxf-viewer-MPL-2.0.txt; source: https://github.com/vagran/dxf-viewer) |
| opentype.js | 1.3.4 | MIT |
| earcut | 3.0.x | ISC |
| loglevel | 1.9.x | MIT |
| Noto Sans (fonts/*.woff, from @fontsource/noto-sans) | 5.x | SIL OFL 1.1 (see fonts/LICENSE-Noto-Sans-OFL.txt) |

dxf-viewer is used unmodified, so the MPL-2.0 file-level obligations are met by shipping its license and the link to
its source.
