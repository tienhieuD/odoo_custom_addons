# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Office Preview: DOCX, DOC, XLSX, XLS, PPTX, PPT, CSV, TSV",
    "version": "17.0.1.0.2",
    "summary": "Preview Word, Excel and PowerPoint files (docx, xlsx, pptx; older doc, xls, ppt with limited support) and csv/tsv inside Odoo, with search. Your documents never leave your Odoo server.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Preview xlsx (grid, merged cells, charts, images, shapes), docx (pages, tables, images) and pptx (slides) with the MIT-licensed silurus OOXML viewer, bundled in the module. Rendering happens in the browser inside a sandboxed iframe; no CDN, no Google Fonts, nothing is sent outside your server. Macro-enabled and template files (xlsm, xltx, xltm, docm, dotx, dotm, pptm, ppsx, ppsm, potx, potm) open the same way; macros are never run. Files attached to the chatter and files held in binary fields of any record open the same way, with a search bar. Delimited text files (csv, tsv) are shown as a sheet where every cell stays text. The older formats doc, xls and ppt are also opened, with limited support: the preview shows a warning, some files may display incorrectly or fail to open, and the dialog then offers a Download button.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "price": 80,
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_office/static/src/js/*.js",
            "dwo_attpreview_office/static/src/xml/*.xml",
        ],
        "web.assets_tests": ["dwo_attpreview_office/static/tests/tours/*.js"],
    },
    "currency": "EUR",
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
