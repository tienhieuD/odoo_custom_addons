# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import html as html_lib
import re

from lxml import etree
from lxml import html as lxml_html

# Odoo 17: _() from odoo (env._ only exists from 18)
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.mail import html_sanitize

from odoo.addons.dwo_attpreview_core.remote_image import mark_bad_images, restore_bad_images

from ..parsers import MailParseError, parse_email, parse_ics, parse_vcf

CID_SRC = re.compile(r"""(src\s*=\s*)(["']?)cid:([^"'\s>]+)\2""", re.I)
# what a sanitized body may still load from outside: pictures, sources sets, backgrounds, CSS url()
REMOTE_ATTR = re.compile(r"""\s(?:src|srcset|background|poster|lowsrc|dynsrc)\s*=\s*(["'])(?!data:)[^"']+\1""", re.I)
# a remote picture of the body (after html_sanitize, attributes are double quoted): loaded through the server (#79)
REMOTE_IMG = re.compile(r"""<img\b([^>]*?)\ssrc="(https?://[^"]+)"([^>]*)>""", re.I)
SRCSET = re.compile(r'\ssrcset="[^"]*"', re.I)
MAX_REMOTE_IMAGES = 100
IMG_WITHOUT_SRC = re.compile(r"""<img\b(?![^>]*\ssrc\s*=\s*["']data:)[^>]*>""", re.I)
CSS_URL = re.compile(r"""url\(\s*(['"]?)(?!data:)[^)]*\1\s*\)""", re.I)
# email HTML colours cells with bgcolor="" and "background: #fff" shorthands; html_sanitize keeps only
# background-color: turn them into it first (white text on a coloured header would become invisible otherwise)
BACKGROUND = re.compile(r"(?<![-\w])background\s*:\s*([^;]+)", re.I)
COLOR = re.compile(r"#[0-9a-f]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|\b[a-z]{3,20}\b", re.I)
NOT_COLORS = {"url", "none", "repeat", "no", "center", "top", "left", "right", "bottom", "fixed", "scroll",
              "inherit", "initial", "unset", "cover", "contain", "auto", "padding", "border", "content", "local",
              "space", "round", "box", "x", "y"}
MAX_INLINE_IMAGE = 3 * 1024 * 1024
MAX_INLINE_TOTAL = 15 * 1024 * 1024


def _clean(value):
    """JSON-safe text: lone surrogates (damaged UTF-16) and NUL characters replaced."""
    if isinstance(value, str):
        return value.encode("utf-8", "replace").decode("utf-8").replace("\x00", "")
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


def _background_color(match):
    for token in COLOR.findall(re.sub(r"url\([^)]*\)", " ", match.group(1))):
        if token.split("(")[0].lower() not in NOT_COLORS and not token.lower().startswith(("repeat", "no-")):
            return "background-color:%s" % token
    return ""


def _keep_backgrounds(html):
    """``bgcolor`` attributes and ``background`` shorthands -> ``background-color`` (see BACKGROUND)."""
    try:
        doc = lxml_html.document_fromstring(html)
    except (etree.ParserError, ValueError):
        return html
    changed = False
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        style = el.get("style") or ""
        bgcolor = (el.attrib.pop("bgcolor", None) or "").strip()
        if bgcolor and COLOR.fullmatch(bgcolor):
            style = "background-color:%s;%s" % (bgcolor, style)
        if "background" in style.lower():
            style = BACKGROUND.sub(_background_color, style)
        if style != (el.get("style") or ""):
            el.set("style", style)
            changed = True
    return lxml_html.tostring(doc, encoding="unicode") if changed else html


class AttPreviewEngineMail(models.AbstractModel):
    _name = "dwo.attpreview.engine.mail"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine: email"

    _dwo_engine_code = "mail"
    _dwo_engine_label = "Email (EML, MSG), calendar (ICS), contact (VCF)"
    _dwo_engine_extensions = ("eml", "emlx", "msg", "oft", "ics", "vcf")
    _dwo_engine_output = "json"
    _dwo_engine_priority = 10
    _dwo_engine_version = "3"

    _dwo_engine_size_groups = (
        ("mail_message", ("eml", "emlx", "msg", "oft"), 30),
        ("mail_card", ("ics", "vcf"), 5),
    )
    _dwo_engine_dialog_width = "medium"  # an email or a card reads better in a narrower window

    # --- engine API ---------------------------------------------------------
    def _dwo_render(self, content, filename):
        ext = self._dwo_ext(filename)
        if ext == "ics":
            data = parse_ics(content)
        elif ext == "vcf":
            data = parse_vcf(content)
        else:
            data = self._dwo_mail_result(self._dwo_mail_parse(content, filename))
        return {"type": "json", "data": _clean(data)}

    def _dwo_extract_part(self, content, filename, index):
        if self._dwo_ext(filename) in ("ics", "vcf"):
            return None
        attachments = self._dwo_mail_parse(content, filename)["attachments"]
        if not 0 <= index < len(attachments):
            return None
        return attachments[index]["name"], attachments[index]["data"]

    # --- helpers --------------------------------------------------------------
    @staticmethod
    def _dwo_ext(filename):
        return filename.rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""

    def _dwo_mail_parse(self, content, filename):
        try:
            return parse_email(content, filename)
        except MailParseError:
            raise UserError(_("This file is not a readable email, or it is damaged."))

    def _dwo_mail_result(self, mail):
        body, used_cids, remote, remote_images = self._dwo_mail_body(mail)
        attachments = [
            {"index": i, "name": a["name"], "mimetype": a["mimetype"], "size": len(a["data"] or b"")}
            for i, a in enumerate(mail["attachments"])
            if not (a.get("content_id") and a["content_id"] in used_cids)  # pictures shown in the body
        ]
        return {
            "kind": "email",
            "format": mail["format"],
            "subject": mail["subject"], "from": mail["from"], "to": mail["to"], "cc": mail["cc"],
            "bcc": mail["bcc"], "reply_to": mail["reply_to"], "date": mail["date"],
            "body_html": body,
            "body_text": "" if body else (mail.get("text") or ""),
            "remote_blocked": remote,
            # pictures of the body hosted on the internet: <img data-dwo-remote="N" hidden ...> in body_html,
            # loaded by the viewer through /dwo_attpreview_mail/remote_image (never by the browser itself)
            "remote_images": len(remote_images),
            "remote_insecure": sum(1 for url in remote_images if not url.lower().startswith("https:")),
            "attachments": attachments,
        }

    def _dwo_remote_images(self, content, filename):
        """URLs of the remote pictures of the body, in the order of their ``data-dwo-remote`` index."""
        if self._dwo_ext(filename) in ("ics", "vcf"):
            return []
        return self._dwo_mail_body(self._dwo_mail_parse(content, filename))[3]

    def _dwo_mail_body(self, mail):
        """The HTML body, safe to show in the sandboxed frame of the viewer: pictures of the email (``cid:``)
        become ``data:`` URIs, Odoo's ``html_sanitize`` removes scripts, event handlers, forms and unsafe
        styles. Each remaining ``<img>`` hosted on the internet loses its address and becomes
        ``<img data-dwo-remote="N" hidden ...>`` (the viewer loads it through the server); every other reference
        to an outside resource (source sets, backgrounds, CSS ``url()``) is removed.
        Returns ``(html, content ids used, whether something remote was found, remote picture URLs)``."""
        html = mail.get("html")
        if not html:
            return "", set(), False, []
        images, total = {}, 0
        for att in mail["attachments"]:
            cid, data = att.get("content_id"), att.get("data") or b""
            if cid and att["mimetype"].startswith("image/") and att["mimetype"] != "image/svg+xml" \
                    and len(data) <= MAX_INLINE_IMAGE and total + len(data) <= MAX_INLINE_TOTAL:
                images[cid] = "data:%s;base64,%s" % (att["mimetype"], base64.b64encode(data).decode())
                total += len(data)
        used = set()

        def inline(match):
            cid = match.group(3)
            if cid in images:
                used.add(cid)
                return '%s"%s"' % (match.group(1), images[cid])
            return '%s""' % match.group(1)

        html = CID_SRC.sub(inline, html)
        html, bad_alts = mark_bad_images(html)  # a script, file: or path as the address: shown as an error (#87)
        html = _keep_backgrounds(html)
        html = str(html_sanitize(html, sanitize_attributes=True, sanitize_style=True, sanitize_form=True,
                                 strip_classes=False))
        html = restore_bad_images(html, bad_alts)
        remote_urls = []

        def mark(match):
            if len(remote_urls) >= MAX_REMOTE_IMAGES:
                return ""
            remote_urls.append(html_lib.unescape(match.group(2)))
            rest = SRCSET.sub("", match.group(1) + match.group(3))
            return '<img data-dwo-remote="%d" hidden%s>' % (len(remote_urls) - 1, rest)

        marked = REMOTE_IMG.sub(mark, html)
        cleaned = REMOTE_ATTR.sub("", marked)
        cleaned = CSS_URL.sub("none", cleaned)
        remote = bool(remote_urls) or cleaned != marked
        cleaned = IMG_WITHOUT_SRC.sub(
            lambda m: m.group(0) if "data-dwo-remote=" in m.group(0) or "data-dwo-bad=" in m.group(0) else "", cleaned)  # no broken pictures
        return cleaned, used, remote, remote_urls
