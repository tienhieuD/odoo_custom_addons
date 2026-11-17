# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Archive Preview: ZIP, RAR, 7Z, TAR",
    "version": "17.0.1.0.0",
    "summary": "Browse ZIP, RAR, 7Z and TAR archives in Odoo as a folder tree and preview the files inside. Keywords: zip preview, preview zip, zip viewer, open zip, rar preview, preview rar, rar viewer, open rar, 7z preview, 7z viewer, tar preview, tar.gz viewer, archive preview, archive viewer, compressed file preview, zip file browser, file tree, folder tree.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Shows the content of zip, tar, tar.gz, "
                   "tar.bz2, tar.xz, gz, rar and 7z files as a folder tree (fast with tens of thousands of files) and "
                   "opens each file inside with the preview engines installed, without extracting the archive. "
                   "No extra installation for zip and tar; rar files inside are opened when unrar is on the server, "
                   "7z archives when the py7zr Python package is installed.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_archive/static/src/js/*.js",
            "dwo_attpreview_archive/static/src/xml/*.xml",
            "dwo_attpreview_archive/static/src/scss/*.scss",
        ],
        "web.assets_tests": ["dwo_attpreview_archive/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "price": 25,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
