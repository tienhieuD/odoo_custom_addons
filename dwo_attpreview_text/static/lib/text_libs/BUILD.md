# text_libs.min.js

One file with the libraries of the text viewer, loaded on demand (only when a text file is opened, `loadJS`) as the
global `DwoTextLibs`. Shipped unmodified (licenses in this folder). No CDN: the file is served by Odoo with the module.
Size: 322 KB (107 KB gzipped).

| Library | Version | License | Used for |
|---|---|---|---|
| [highlight.js](https://github.com/highlightjs/highlight.js) | 11.12.0 | BSD-3-Clause | syntax colours (Raw view, code blocks of Markdown and notebooks) |
| [markdown-it](https://github.com/markdown-it/markdown-it) | 15.0.3 | MIT | Markdown preview and outline (raw HTML off) |
| entities, linkify-it, mdurl, uc.micro, punycode.js | 8.1.0, 6.1.0, 2.1.0, 3.0.0, 2.3.1 | BSD-2-Clause / MIT | dependencies of markdown-it |
| [js-yaml](https://github.com/nodeca/js-yaml) | 5.5.0 | MIT | YAML tree (default safe schema: no JavaScript types) |
| [smol-toml](https://github.com/squirrelchat/smol-toml) | 1.9.1 | BSD-3-Clause | TOML tree |

highlight.js languages included (38): xml (HTML, SVG, Vue), markdown, json, yaml, ini (also TOML), properties,
python, javascript, typescript, css, scss, sql, bash, powershell, dos, java, kotlin, swift, c, cpp, csharp, go, rust,
php, ruby, dart, lua, r, perl, scala, groovy, gradle, dockerfile, makefile, nginx, diff, latex, plaintext.
The GitHub light theme of highlight.js is bundled as text (`hljsCss`) for the sandboxed preview frame; the same
colours are in `static/src/scss/text_viewer.scss` for the Raw view.

Parsed on the server instead (Python, no extra library): encoding detection, XML tree (`safe_xml` of the core:
entities, DTD and network off), HTML sanitizing (`html_sanitize` of Odoo), Jupyter notebooks. JSON is read by the
browser (`JSON.parse`, comments and trailing commas removed for JSONC); INI / env / properties, logs, diffs,
subtitles and PO files by small readers in `static/src/js/formats.js`.

Build again (from an empty folder, Node 20+):

    npm init -y && npm install highlight.js@11.12.0 markdown-it@15.0.3 js-yaml@5.5.0 smol-toml@1.9.1 esbuild
    cp dwo_attpreview_text/static/lib/text_libs/entry.js .
    npx esbuild entry.js --bundle --format=iife --global-name=DwoTextLibs --minify --target=es2020 \
        --legal-comments=none --loader:.css=text --outfile=text_libs.min.js
