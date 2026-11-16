# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Readers of email, calendar and contact files. Pure Python (standard library + the shipped olefile), no Odoo:
they return plain data, the engine (models/engine.py) sanitizes the HTML and builds the result of the preview.

An email is a dict::

    {"format": "eml"|"msg", "subject", "from", "to", "cc", "bcc", "reply_to", "date" (ISO 8601 or raw text),
     "html": str|None, "text": str|None,
     "attachments": [{"name", "mimetype", "data": bytes, "content_id": str|None, "inline": bool}]}
"""
from .common import MAX_ATTACHMENTS, MAX_DEPTH, MailParseError  # noqa: F401
from .mime import is_ole, parse_eml, parse_emlx  # noqa: F401
from .msg import parse_msg  # noqa: F401
from .cards import parse_ics, parse_vcf  # noqa: F401


def parse_email(content, filename):
    """Read an .eml, .emlx, .msg or .oft file. The first bytes decide (an Outlook file renamed .eml, or a MIME
    email saved as .msg, still opens), then the extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
    if is_ole(content):
        return parse_msg(content)
    if ext == "emlx":
        return parse_emlx(content)
    return parse_eml(content)
