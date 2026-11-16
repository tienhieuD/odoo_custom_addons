# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""MIME emails (.eml) and Apple Mail (.emlx), with the standard library ``email`` package (the one Odoo uses to
read incoming mail). Damaged charsets and headers fall back to a lenient decoding instead of failing."""
import re
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

from .common import MAX_ATTACHMENTS, MailParseError, guess_type, one_line, safe_name

OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
EMLX_HEAD = re.compile(rb"\s*(\d+)[ \t]*\r?\n")
HEADERS = (("subject", "Subject"), ("from", "From"), ("to", "To"), ("cc", "Cc"), ("bcc", "Bcc"),
           ("reply_to", "Reply-To"))


def is_ole(content):
    return content[:8] == OLE_MAGIC


def _header(msg, name):
    """A decoded header, even when it is malformed (the strict parser of ``policy.default`` can raise)."""
    try:
        value = msg.get(name)
        return one_line(value) if value is not None else ""
    except Exception:  # noqa: BLE001 - any parser defect: read the raw value
        pass
    for key, raw in getattr(msg, "_headers", []):
        if key.lower() == name.lower():
            try:
                return one_line(str(make_header(decode_header(str(raw)))))
            except Exception:  # noqa: BLE001
                return one_line(raw)
    return ""


def _date(msg):
    raw = _header(msg, "Date")
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).isoformat()
    except (TypeError, ValueError, IndexError, OverflowError):
        return raw


def _text(part):
    """Text of a text/* part, decoded with its charset; an unknown or wrong charset falls back to UTF-8."""
    try:
        return part.get_content()
    except Exception:  # noqa: BLE001 - LookupError (unknown charset), UnicodeError, defects
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, "replace")
        except LookupError:
            return payload.decode("utf-8", "replace")


def _leaves(part, depth=0):
    """The parts that are not containers. An attached email (message/rfc822) is one leaf, not opened here."""
    if depth > 50:
        return
    if part.get_content_type() == "message/rfc822" or not part.is_multipart():
        yield part
        return
    try:
        children = list(part.iter_parts())
    except Exception:  # noqa: BLE001
        children = []
    for child in children:
        yield from _leaves(child, depth + 1)


def _bytes_of(part):
    if part.get_content_type() == "message/rfc822":
        payload = part.get_payload()
        inner = payload[0] if isinstance(payload, list) and payload else None
        if inner is not None:
            try:
                return inner.as_bytes(policy=policy.SMTP)
            except Exception:  # noqa: BLE001
                return bytes(inner)
        return part.get_payload(decode=True) or b""
    return part.get_payload(decode=True) or b""


def parse_eml(content):
    msg = BytesParser(policy=policy.default).parsebytes(content)
    if not msg.keys():
        raise MailParseError("no email headers")
    mail = {key: _header(msg, name) for key, name in HEADERS}
    mail.update(format="eml", date=_date(msg), html=None, text=None, attachments=[])
    html_part = text_part = None
    for part in _leaves(msg):
        ctype = part.get_content_type()
        disposition = (part.get_content_disposition() or "").lower()
        filename = None
        try:
            filename = part.get_filename()
        except Exception:  # noqa: BLE001
            filename = None
        is_body = disposition != "attachment" and not filename
        if is_body and ctype == "text/html" and html_part is None:
            html_part = part
            continue
        if is_body and ctype == "text/plain" and text_part is None:
            text_part = part
            continue
        if len(mail["attachments"]) >= MAX_ATTACHMENTS:
            continue
        data = _bytes_of(part)
        index = len(mail["attachments"])
        if ctype == "message/rfc822" and not filename:
            inner = part.get_payload()
            subject = _header(inner[0], "Subject") if isinstance(inner, list) and inner else ""
            filename = (subject or "message")[:100] + ".eml"
        name = safe_name(filename, index, ctype)
        cid = (part.get("Content-ID") or "").strip().strip("<>") or None
        mail["attachments"].append({
            "name": name, "mimetype": guess_type(name, ctype), "data": data, "content_id": cid,
            "inline": disposition == "inline" and bool(cid),
        })
    if html_part is not None:
        mail["html"] = _text(html_part)
    if text_part is not None:
        mail["text"] = _text(text_part)
    return mail


def parse_emlx(content):
    """Apple Mail: a line with the length of the message, the MIME message, then a property list."""
    match = EMLX_HEAD.match(content)
    if not match:
        return parse_eml(content)
    start = match.end()
    return parse_eml(content[start:start + int(match.group(1))])
