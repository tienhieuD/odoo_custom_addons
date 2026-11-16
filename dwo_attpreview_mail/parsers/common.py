# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Shared helpers of the readers."""
import mimetypes
import re
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.utils import format_datetime

MAX_DEPTH = 20  # Outlook messages attached to Outlook messages, level after level (same bound as the Core)
MAX_ATTACHMENTS = 500
CONTROL = re.compile(r"[\x00-\x1f\x7f]+")


class MailParseError(ValueError):
    """The file is not a readable email (the engine turns it into a clean message for the user)."""


def one_line(value):
    """A header value on one line, without control characters."""
    return CONTROL.sub(" ", str(value or "")).strip()


def safe_name(name, index, mimetype=None):
    """A file name without folders or control characters; ``attachment-N.ext`` when there is none."""
    name = one_line(name).replace("\\", "/").rsplit("/", 1)[-1].strip(" .")
    if not name:
        ext = mimetypes.guess_extension(mimetype or "") or ""
        name = "attachment-%d%s" % (index + 1, ext)
    return name[:200]


def guess_type(name, mimetype=None):
    mimetype = (mimetype or "").split(";")[0].strip().lower()
    if not mimetype or mimetype == "application/octet-stream":
        mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    return mimetype


def to_eml(mail):
    """Bytes of an .eml file made from a parsed email (for an Outlook message attached to an Outlook message)."""
    msg = EmailMessage(policy=policy.SMTP)
    date = mail.get("date") or ""
    try:
        date = format_datetime(datetime.fromisoformat(date)) if date else ""
    except ValueError:
        pass
    for header, value in (("Subject", mail.get("subject")), ("From", mail.get("from")), ("To", mail.get("to")),
                          ("Cc", mail.get("cc")), ("Date", date)):
        if value:
            try:
                msg[header] = one_line(value)
            except (ValueError, TypeError, IndexError):
                pass
    text, html = mail.get("text"), mail.get("html")
    if html:
        msg.set_content(text or "")
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(text or "")
    for att in mail.get("attachments") or []:
        maintype, _, subtype = (att.get("mimetype") or "application/octet-stream").partition("/")
        if maintype == "text":  # set_content wants str for text parts: keep the bytes as they are
            maintype, subtype = "application", "octet-stream"
        try:
            msg.add_attachment(att["data"], maintype=maintype, subtype=subtype or "octet-stream",
                               filename=att.get("name") or "attachment")
        except (ValueError, TypeError):
            continue
    return msg.as_bytes()
