# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Outlook messages (.msg) and templates (.oft): an OLE compound file read with the shipped olefile, following
the published Microsoft specification [MS-OXMSG]. Only the properties a reader needs are read: subject, sender,
recipients, date, bodies (plain, HTML, compressed RTF) and attachments. An Outlook message attached to the message
becomes an .eml file (so it can be previewed in its turn). Nothing in the file is executed."""
import codecs
import io
import re
import struct
from datetime import datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser

from ..thirdparty.olefile import OleFileIO
from .common import MAX_ATTACHMENTS, MAX_DEPTH, MailParseError, guess_type, one_line, safe_name, to_eml
from .rtf import decompress_rtf, rtf_to_text

# property ids ([MS-OXPROPS])
SUBJECT, SENDER_NAME, SENDER_EMAIL, SENDER_SMTP = 0x0037, 0x0C1A, 0x0C1F, 0x5D01
SENT_REPR_NAME, SENT_REPR_EMAIL, TRANSPORT_HEADERS = 0x0042, 0x0065, 0x007D
DISPLAY_TO, DISPLAY_CC, DISPLAY_BCC = 0x0E04, 0x0E03, 0x0E02
SUBMIT_TIME, DELIVERY_TIME, CREATION_TIME = 0x0039, 0x0E06, 0x3007
BODY, BODY_HTML, RTF_COMPRESSED = 0x1000, 0x1013, 0x1009
MESSAGE_CODEPAGE, INTERNET_CPID, MESSAGE_LOCALE = 0x3FFD, 0x3FDE, 0x3FF1
DISPLAY_NAME, EMAIL_ADDRESS, SMTP_ADDRESS, RECIPIENT_TYPE = 0x3001, 0x3003, 0x39FE, 0x0C15
ATTACH_DATA, ATTACH_FILENAME, ATTACH_METHOD, ATTACH_LONG_FILENAME = 0x3701, 0x3704, 0x3705, 0x3707
ATTACH_MIME, ATTACH_CONTENT_ID, ATTACH_HIDDEN = 0x370E, 0x3712, 0x7FFE
EMBEDDED = "__substg1.0_3701000D"  # an Outlook message attached to the message

PT_LONG, PT_BOOLEAN, PT_SYSTIME = 0x0003, 0x000B, 0x0040
CODEPAGES = {
    65001: "utf-8", 1200: "utf-16-le", 1201: "utf-16-be", 20127: "ascii", 28591: "latin-1", 28592: "iso8859-2",
    28593: "iso8859-3", 28594: "iso8859-4", 28595: "iso8859-5", 28596: "iso8859-6", 28597: "iso8859-7",
    28598: "iso8859-8", 28599: "iso8859-9", 28603: "iso8859-13", 28605: "iso8859-15", 20866: "koi8-r",
    21866: "koi8-u", 50220: "iso2022-jp", 50221: "iso2022-jp", 50222: "iso2022-jp", 51932: "euc-jp",
    51949: "euc-kr", 54936: "gb18030", 936: "gbk", 950: "big5", 949: "cp949", 932: "cp932",
}
# Windows code page of the language of the message (when the message gives no code page for its 8 bit strings)
LOCALE_CODEPAGES = {
    1025: 1256, 1026: 1251, 1028: 950, 1029: 1250, 1032: 1253, 1037: 1255, 1038: 1250, 1041: 932, 1042: 949,
    1045: 1250, 1048: 1250, 1049: 1251, 1050: 1250, 1051: 1250, 1054: 874, 1055: 1254, 1058: 1251, 1059: 1251,
    1060: 1250, 1061: 1257, 1062: 1257, 1063: 1257, 1066: 1258, 1087: 1251, 2052: 936, 3076: 950, 4100: 936,
    5124: 950,
}
META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?([A-Za-z0-9_\-]+)""", re.I)


def _codec(codepage, default="cp1252"):
    if not codepage:
        return default
    name = CODEPAGES.get(codepage) or "cp%d" % codepage
    try:
        return codecs.lookup(name).name
    except LookupError:
        return default


def _filetime(value):
    if not value:
        return ""
    try:
        return (datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=value // 10)).isoformat()
    except (OverflowError, ValueError):
        return ""


class _Storage:
    """One message, attachment or recipient storage of the file."""

    def __init__(self, ole, path, header_size):
        self.ole, self.path = ole, list(path)
        self.fixed = self._fixed(header_size)

    def _stream(self, name):
        full = "/".join(self.path + [name])
        if not self.ole.exists(full):
            return None
        return self.ole.openstream(full).read()

    def _fixed(self, header_size):
        """Fixed size properties (numbers, dates, flags) of the __properties_version1.0 stream."""
        data = self._stream("__properties_version1.0") or b""
        out = {}
        for pos in range(header_size, len(data) - 15, 16):
            tag, _flags, value = struct.unpack_from("<IIQ", data, pos)
            ptype, pid = tag & 0xFFFF, tag >> 16
            if ptype in (PT_LONG, PT_BOOLEAN):
                out[pid] = value & 0xFFFFFFFF
            elif ptype == PT_SYSTIME:
                out[pid] = value
        return out

    def raw(self, pid):
        """Bytes of a variable size property and its type (``"001F"`` unicode, ``"001E"`` 8 bit, ``"0102"``)."""
        for ptype in ("001F", "001E", "0102"):
            data = self._stream("__substg1.0_%04X%s" % (pid, ptype))
            if data is not None:
                return data, ptype
        return None, None

    def text(self, pid, codec):
        data, ptype = self.raw(pid)
        if data is None:
            return ""
        if ptype == "001F":
            return data.decode("utf-16-le", "replace").rstrip("\x00")
        return data.decode(codec, "replace").rstrip("\x00")

    def children(self, prefix):
        """Names of the storages directly inside this one whose name starts with ``prefix``."""
        depth = len(self.path)
        names = set()
        for entry in self.ole.listdir(streams=False, storages=True):
            if len(entry) == depth + 1 and entry[:depth] == self.path and entry[-1].startswith(prefix):
                names.add(entry[-1])
        return sorted(names)


EMAIL = re.compile(r"^[^@\s/<>]+@[^@\s/<>]+$")


def _address(name, email):
    """``Name <email>``; an Exchange address (/O=.../CN=...) is no email address: the name alone."""
    name, email = one_line(name), one_line(email)
    if email and EMAIL.match(email) and email.lower() != name.lower():
        return "%s <%s>" % (name, email) if name else email
    return name or (email if EMAIL.match(email or "") else "")


def _read_message(ole, path, header_size, depth):
    msg = _Storage(ole, path, header_size)
    # 8 bit strings follow the code page of the message; the HTML body follows the internet code page (it wins
    # over a <meta charset> of the HTML, which Outlook does not always keep right)
    locale = msg.fixed.get(MESSAGE_LOCALE)
    codec = _codec(msg.fixed.get(MESSAGE_CODEPAGE) or LOCALE_CODEPAGES.get(locale, 1252 if locale else None)
                   or msg.fixed.get(INTERNET_CPID))
    internet_cp = msg.fixed.get(INTERNET_CPID)

    headers = None
    raw_headers = msg.text(TRANSPORT_HEADERS, codec)
    if raw_headers:
        try:
            headers = BytesParser(policy=policy.default).parsebytes(raw_headers.encode("utf-8", "replace"),
                                                                     headersonly=True)
        except Exception:  # noqa: BLE001
            headers = None

    def header(name):
        if headers is None:
            return ""
        try:
            return one_line(headers.get(name) or "")
        except Exception:  # noqa: BLE001
            return ""

    sender_email = msg.text(SENDER_SMTP, codec) or msg.text(SENDER_EMAIL, codec) or msg.text(SENT_REPR_EMAIL, codec)
    sender = _address(msg.text(SENDER_NAME, codec) or msg.text(SENT_REPR_NAME, codec), sender_email)
    recipients = {1: [], 2: [], 3: []}
    for name in msg.children("__recip_version1.0_"):
        rec = _Storage(ole, path + [name], 8)
        email = rec.text(SMTP_ADDRESS, codec) or rec.text(EMAIL_ADDRESS, codec)
        recipients.setdefault(rec.fixed.get(RECIPIENT_TYPE, 1), []).append(_address(rec.text(DISPLAY_NAME, codec), email))

    date = (_filetime(msg.fixed.get(SUBMIT_TIME)) or _filetime(msg.fixed.get(DELIVERY_TIME)) or header("Date")
            or _filetime(msg.fixed.get(CREATION_TIME)))
    mail = {
        "format": "msg",
        "subject": one_line(msg.text(SUBJECT, codec)),
        "from": sender or header("From"),
        "to": ", ".join(r for r in recipients[1] if r) or one_line(msg.text(DISPLAY_TO, codec)) or header("To"),
        "cc": ", ".join(r for r in recipients[2] if r) or one_line(msg.text(DISPLAY_CC, codec)) or header("Cc"),
        "bcc": ", ".join(r for r in recipients[3] if r) or one_line(msg.text(DISPLAY_BCC, codec)),
        "reply_to": header("Reply-To"),
        "date": date,
        "html": None,
        "text": msg.text(BODY, codec) or None,
        "attachments": [],
    }

    data, ptype = msg.raw(BODY_HTML)
    if data is not None:
        if ptype == "001F":
            mail["html"] = data.decode("utf-16-le", "replace").rstrip("\x00")
        else:
            charset = _codec(internet_cp) if internet_cp else None
            match = META_CHARSET.search(data[:4096])
            if charset is None and match:
                try:
                    charset = codecs.lookup(match.group(1).decode("ascii")).name
                except LookupError:
                    charset = None
            charset = charset or (_codec(msg.fixed.get(MESSAGE_CODEPAGE)) if msg.fixed.get(MESSAGE_CODEPAGE)
                                  else "utf-8")
            mail["html"] = data.decode(charset, "replace").rstrip("\x00")
    if not mail["html"] and not mail["text"]:
        rtf, _ptype = msg.raw(RTF_COMPRESSED)
        if rtf:
            try:
                mail["text"] = rtf_to_text(decompress_rtf(rtf), codec) or None
            except ValueError:
                pass

    for index, name in enumerate(msg.children("__attach_version1.0_")):
        if index >= MAX_ATTACHMENTS:
            break
        att = _Storage(ole, path + [name], 8)
        method = att.fixed.get(ATTACH_METHOD, 1)
        mimetype = one_line(att.text(ATTACH_MIME, codec))
        filename = (att.text(ATTACH_LONG_FILENAME, codec) or att.text(ATTACH_FILENAME, codec)
                    or att.text(DISPLAY_NAME, codec))
        position = len(mail["attachments"])
        if method == 5 and depth < MAX_DEPTH and att.children(EMBEDDED):
            inner = _read_message(ole, path + [name, EMBEDDED], 24, depth + 1)
            content = to_eml(inner)
            filename = (inner.get("subject") or filename or "message")[:100] + ".eml"
            mimetype = "message/rfc822"
        else:
            content, _ptype = att.raw(ATTACH_DATA)
            if content is None:
                continue  # an OLE object or a link: nothing a reader can open
        filename = safe_name(filename, position, mimetype)
        mail["attachments"].append({
            "name": filename, "mimetype": guess_type(filename, mimetype), "data": content,
            "content_id": one_line(att.text(ATTACH_CONTENT_ID, codec)).strip("<>") or None,
            "inline": bool(att.fixed.get(ATTACH_HIDDEN)),
        })
    return mail


def parse_msg(content):
    try:
        ole = OleFileIO(io.BytesIO(content))
    except Exception as e:  # noqa: BLE001 - olefile raises various errors on damaged files
        raise MailParseError("not a readable Outlook file") from e
    try:
        if not ole.exists("__properties_version1.0"):
            raise MailParseError("not an Outlook message")
        return _read_message(ole, [], 32, 0)
    except MailParseError:
        raise
    except Exception as e:  # noqa: BLE001
        raise MailParseError("damaged Outlook message") from e
    finally:
        ole.close()
