# tree_libs.min.js

One file with the two tree libraries of the shared tree view (`static/src/js/tree_view.js`, used by the archive and
text engines), loaded with the backend assets as the global `DwoTreeLibs`. Shipped unmodified
(MIT licenses in this folder). No CDN: the file is served by Odoo with the module.

| Library | Version | License | Used for |
|---|---|---|---|
| [@headless-tree/core](https://github.com/lukasbach/headless-tree) | 1.8.0 | MIT | tree state: expand/collapse, focus, keyboard (arrows, Home/End), ARIA attributes |
| [@tanstack/virtual-core](https://github.com/TanStack/virtual) | 3.19.11 | MIT | virtual scrolling: only the visible rows are in the page |

The rows are drawn by the core (OWL, `static/src/js/tree_view.js`, component `DwoTreeView`), not by the libraries.
Moved from `dwo_attpreview_archive` to the core in 19.0.1.3.0 (#83). Engines may also use `DwoTreeLibs.Virtualizer`
for their own virtual lists (the text engine does for the lines of a file).

Build again (from an empty folder, Node 20+):

    npm init -y && npm install @headless-tree/core@1.8.0 @tanstack/virtual-core@3.19.11 esbuild
    cp dwo_attpreview_core/static/lib/tree_libs/entry.js .
    npx esbuild entry.js --bundle --format=iife --global-name=DwoTreeLibs --minify --target=es2020 \
        --legal-comments=none --outfile=tree_libs.min.js
