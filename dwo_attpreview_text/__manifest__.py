# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Text & Code Preview: MD, HTML, XML, JSON, YAML, LOG",
    "version": "17.0.1.1.1",
    "summary": "Preview text and code files in Odoo: raw text with syntax colours, rendered Markdown and HTML, JSON, XML and YAML trees, logs and diffs. Keywords: text preview, text file viewer, code viewer, source code preview, syntax highlighting, markdown preview, preview markdown, markdown viewer, html preview, xml viewer, xml tree, json viewer, json tree, json preview, yaml viewer, log viewer, log file viewer, diff viewer, patch viewer, ipynb viewer, jupyter notebook viewer, po file viewer, srt viewer.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Opens text, code and data files in the "
                   "preview dialog: Raw (line numbers, syntax colours, wrap, find, go to line, copy), Preview "
                   "(Markdown, HTML, Jupyter notebooks, logs coloured by level, diffs side by side, subtitles, PO "
                   "translations) and Structure (JSON, XML, YAML, TOML, INI trees, Markdown outline), fast with very "
                   "large files. HTML and Markdown are shown in a sandboxed frame: no script of the file runs, pictures "
                   "from the internet are downloaded by your Odoo server (never by the browser) and only real "
                   "pictures are shown, and a link asks for confirmation before it opens in a new tab. No CDN.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "data": ["data/ir_config_parameter.xml", "views/res_config_settings_views.xml"],
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_text/static/src/js/*.js",
            "dwo_attpreview_text/static/src/xml/*.xml",
            "dwo_attpreview_text/static/src/scss/*.scss",
        ],
        "web.assets_tests": ["dwo_attpreview_text/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "price": 15,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
