# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Office Preview: DOCX, XLSX, PPTX, ODT, ODS, ODP, DOC, XLS, PPT, CSV",
    "version": "18.0.1.1.0",
    "summary": "Preview Word, Excel, PowerPoint, OpenDocument (LibreOffice) and CSV files in Odoo without downloading. Files never leave your Odoo server: no external viewer or service. Keywords: office preview, preview office, ms office preview, document preview, document viewer, docx preview, preview docx, word preview, preview word, xlsx preview, preview xlsx, excel preview, preview excel, excel viewer, pptx preview, powerpoint preview, doc preview, xls preview, ppt preview, odt preview, ods preview, odp preview, libreoffice preview, opendocument viewer, csv preview, csv viewer, office viewer, file preview, attachment preview.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Preview xlsx (grid, merged cells, charts, images, shapes), docx (pages, tables, images) and pptx (slides) with the MIT-licensed silurus OOXML viewer, bundled in the module. Rendering happens in the browser inside a sandboxed iframe; no CDN, no Google Fonts, nothing is sent outside your server. Macro-enabled and template files (xlsm, xltx, xltm, docm, dotx, dotm, pptm, ppsx, ppsm, potx, potm) open the same way; macros are never run. Files attached to the chatter and files held in binary fields of any record open the same way, with a search bar. OpenDocument files saved by LibreOffice and other office suites (odt, ods, odp and the templates ott, ots, otp) open in the same viewers, read directly by the bundled MIT-licensed silurus OpenDocument reader; scripts and macros of the file are never run. Delimited text files (csv, tsv) are shown as a sheet where every cell stays text. The older formats doc, xls and ppt are also opened, with limited support: the preview shows a warning, some files may display incorrectly or fail to open, and the dialog then offers a Download button.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "data": ["views/res_config_settings_views.xml"],
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
