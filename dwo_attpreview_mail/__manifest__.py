# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Email Preview: EML, MSG, ICS, VCF",
    "version": "20.0.2.2.1",
    "live_test_url": "https://demo-attpreview.duotek.io.vn",
    "summary": "Open Outlook MSG and EML emails in Odoo with their attachments, level after level. Keywords: email preview, preview email, eml preview, preview eml, eml viewer, msg preview, preview msg, msg viewer, outlook msg, outlook email, open msg file, email attachment preview, ics preview, calendar invitation, vcf preview, vcard.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Preview .eml, .emlx, .msg and .oft "
                   "emails with headers, body and attachments (each attachment opens in its own preview), .ics "
                   "invitations and .vcf contact cards. Read on your server and shown in an isolated frame; pictures linked "
                   "from the internet are downloaded by your server, never by the browser of the user, and only real pictures are shown (a program or script address gets a visible error). A link asks for confirmation before it opens in a new tab.",
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
