# Secure Text & Code Preview (dwo_attpreview_text)

Engine of **Secure Attachment Preview** (`dwo_attpreview_core`) for text, code and data files. Installing it is all
there is to do: text files open in the preview dialog from the chatter, file fields, attachment lists, archives and
emails (with the archive and email engines).

## Using it

- The bar at the top switches between **Preview**, **Structure** and **Raw**; only the views that make sense for the
  file are shown. The info next to it gives the kind of file, encoding, line endings, number of lines and size.
- **Raw**: line numbers and syntax colours. *Wrap* wraps long lines. **Ctrl+F** opens the find bar (Enter: next,
  Shift+Enter: previous, Esc: close). **Ctrl+G** or the *Go to line* box jumps to a line. *Copy* copies the whole text.
- **Structure**: fold and unfold with the mouse or the arrow keys (Home / End go to the first / last row). The filter
  box keeps the rows whose key or value contains the text, with their parents. The bar at the bottom shows the path
  of the selected row (*Copy path*) and, for XML and Markdown, *Show line N in Raw*.
- **Log** preview: click a level (Errors, Warnings, Info, Debug, Other) to hide or show its lines. A line without a
  level (a traceback) belongs to the line above.
- **PO** preview: All / Untranslated / Fuzzy / Translated.

## Limits

- Up to 10 MB of text is shown (the size limit of the core applies first, Settings > Attachment Preview). A larger
  file shows its first 10 MB, without tree.
- Syntax colours up to 1.5 MB or 40 000 lines; larger files are shown plain (a note says so).
- Trees: up to 1 000 000 values (JSON / YAML), 200 000 XML elements. *Expand all* up to 5 000 nodes.
- HTML and Markdown previews never load anything from the internet: remote pictures are replaced by a placeholder.
  Download the file to see them in a browser.
- MDX is shown as Markdown (its components are not run). JSON5 is read as JSON with comments and trailing commas.

## For developers

- Server: `models/engine.py` (engine `text`), `text_tools.py` (kinds of files, encoding, XML tree, HTML, notebooks).
- Browser: `static/src/js/text_viewer.js` (viewer `text` of the registry `dwo_attpreview.viewers`),
  `formats.js` (readers, no OWL), `line_view.js` (virtual list of lines), the tree is `DwoTreeView` of the core.
- Libraries: `static/lib/text_libs/BUILD.md`.
