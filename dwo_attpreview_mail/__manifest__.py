# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Email Preview: EML, MSG, ICS, VCF",
    "version": "19.0.2.1.0",
    "summary": "Open Outlook MSG and EML emails, calendar invitations and contact cards inside Odoo. "
               "Remote pictures load through your server, attachments previewed in place.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Preview .eml, .emlx, .msg and .oft "
                   "emails with headers, body and attachments (each attachment opens in its own preview), .ics "
                   "invitations and .vcf contact cards. Read on your server and shown in an isolated frame; pictures linked "
                   "from the internet are downloaded by your server, never by the browser of the user.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_mail/static/src/js/*.js",
            "dwo_attpreview_mail/static/src/xml/*.xml",
            "dwo_attpreview_mail/static/src/scss/*.scss",
        ],
        "web.assets_tests": ["dwo_attpreview_mail/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "price": 30,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
