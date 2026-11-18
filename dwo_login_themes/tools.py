# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Pure helpers: the notice sanitizer, colour checks and the image processing of the uploads.

Everything here is independent of the Odoo version (the same file is used in 17, 18, 19 and 20).
"""
import base64
import io
import re

from lxml import etree, html as lxml_html
from markupsafe import Markup

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import html_sanitize

# ---------------------------------------------------------------------------------------------------------------
# ir.config_parameter: Odoo 20 replaced get_param / set_param by get_str / set_str
# ---------------------------------------------------------------------------------------------------------------
def icp_get(icp, key):
    """The string value of a system parameter, ``False`` when it is not set."""
    if hasattr(icp, "get_str"):
        return icp.get_str(key, False)
    return icp.get_param(key)


def icp_set(icp, key, value):
    """Set a system parameter (a string); a false value unsets it."""
    value = False if value in (False, None, "") else str(value)
    if hasattr(icp, "set_str"):
        return icp.set_str(key, value)
    return icp.set_param(key, value)


def binary_b64(value):
    """The base64 bytes of the value of a Binary field: bytes in Odoo 17-19, a BinaryValue in Odoo 20; ``b""`` when empty."""
    if not value:
        return b""
    if hasattr(value, "to_base64"):
        value = value.to_base64()
    return value.encode() if isinstance(value, str) else bytes(value)


def attachment_bytes(att):
    """The raw bytes of an attachment (``raw`` is a BinaryValue in Odoo 20)."""
    raw = att.raw
    raw = getattr(raw, "content", raw)
    return bytes(raw) if raw else b""


# ---------------------------------------------------------------------------------------------------------------
# Announcement (notice) HTML
# ---------------------------------------------------------------------------------------------------------------
ALLOWED_TAGS = frozenset("p br b strong i em u ul ol li a h1 h2 h3 h4 span div hr".split())
# the element and everything inside it is dropped (all the other unknown tags are unwrapped: the text stays)
DROP_WITH_CONTENT = frozenset(
    "script style iframe frame frameset object embed applet form input button textarea select option "
    "svg math img picture video audio source track canvas link meta base head title noscript template".split())
ALLOWED_SCHEMES = ("http://", "https://", "mailto:")
MAX_NOTICE_LENGTH = 10000


def _clean_href(href):
    """The href when it is an http(s) or mailto link, else ``None``. Control characters and spaces are removed
    before the check, so ``" JaVa\\tScRiPt:..."`` cannot slip through."""
    flat = re.sub(r"[\x00-\x20\x7f-\x9f]+", "", href or "")
    return flat if flat.lower().startswith(ALLOWED_SCHEMES) else None


def sanitize_notice(src):
    """Return the announcement as a safe ``Markup``: only whitelisted tags, only ``href`` on links (http, https,
    mailto) with ``rel="noopener noreferrer" target="_blank"``, no script, style, iframe, form, image or ``on*``
    attribute. Run it when the setting is saved and again when the login page is rendered."""
    src = (src or "").strip()[:MAX_NOTICE_LENGTH]
    if not src:
        return Markup("")
    # first pass with the sanitizer of Odoo (lxml cleaner), then our own whitelist
    first = html_sanitize(src, silent=True, sanitize_tags=True, sanitize_attributes=True, sanitize_style=False,
                          sanitize_form=True, strip_style=True, strip_classes=True) or ""
    try:
        root = lxml_html.fragment_fromstring(str(first), create_parent="div")
    except (etree.ParserError, ValueError):
        return Markup("")
    _clean_element(root)
    out = Markup.escape(root.text) if root.text else Markup("")
    for child in root:
        out += Markup(etree.tostring(child, encoding="unicode", method="html"))
    return out


def _clean_element(parent):
    for child in list(parent):
        if not isinstance(child.tag, str):  # comment, processing instruction
            _remove_keep_tail(child)
            continue
        tag = child.tag.lower()
        if tag in DROP_WITH_CONTENT:
            _remove_keep_tail(child)
            continue
        _clean_element(child)
        if tag not in ALLOWED_TAGS:
            _unwrap(child)
            continue
        for attr in list(child.attrib):
            if not (tag == "a" and attr == "href"):
                del child.attrib[attr]
        if tag == "a":
            href = _clean_href(child.attrib.get("href"))
            if href:
                child.set("href", href)
                child.set("rel", "noopener noreferrer")
                child.set("target", "_blank")
            else:
                _unwrap(child)


def _remove_keep_tail(el):
    parent = el.getparent()
    tail = el.tail or ""
    prev = el.getprevious()
    if tail:
        if prev is not None:
            prev.tail = (prev.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail
    parent.remove(el)


def _unwrap(el):
    """Replace ``el`` by its content (text and children)."""
    parent = el.getparent()
    index = parent.index(el)
    prev = el.getprevious()
    text = el.text or ""
    if text:
        if prev is not None:
            prev.tail = (prev.tail or "") + text
        else:
            parent.text = (parent.text or "") + text
    children = list(el)
    for offset, child in enumerate(children):
        parent.insert(index + offset, child)
    tail = el.tail or ""
    parent.remove(el)
    if tail:
        last = children[-1] if children else prev
        if last is not None:
            last.tail = (last.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail


# ---------------------------------------------------------------------------------------------------------------
# Values that end up in CSS
# ---------------------------------------------------------------------------------------------------------------
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def safe_color(value, default):
    value = (value or "").strip()
    return value if HEX_COLOR.match(value) else default


def clamp_int(value, low, high, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


# ---------------------------------------------------------------------------------------------------------------
# Uploaded images
# ---------------------------------------------------------------------------------------------------------------
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}  # no SVG (scripts), no GIF/TIFF/BMP
MAX_UPLOAD_BYTES = 6 * 1024 * 1024
MAX_PIXELS = 36 * 1000 * 1000
IMAGE_LIMITS = {  # kind: (max width, max height, output format)
    "bg": (1920, 1920, "WEBP"),
    "logo": (800, 400, "WEBP"),
    "favicon": (128, 128, "PNG"),
}


def process_image(data, kind):
    """Validate an uploaded image (``bytes`` or base64) and return ``(raw bytes, mimetype)`` recompressed.

    Rejects anything that is not a JPEG, PNG or WebP picture, files over 6 MB and huge pixel counts; the picture
    is decoded again and saved as a new file, so nothing but pixels survives (metadata, scripts, polyglots)."""
    from PIL import Image, ImageOps, UnidentifiedImageError
    from PIL import WebPImagePlugin  # noqa: F401  Odoo turns off the lazy loading of the Pillow plugins: WebP must be imported

    if isinstance(data, str):
        data = data.encode()
    try:
        raw = base64.b64decode(data, validate=False)
    except Exception:  # noqa: BLE001
        raise UserError(_("The uploaded file is not a valid image."))
    if not raw:
        raise UserError(_("The uploaded file is empty."))
    if len(raw) > MAX_UPLOAD_BYTES:
        raise UserError(_("The image is too big: the limit is %s MB.", MAX_UPLOAD_BYTES // (1024 * 1024)))
    try:
        probe = Image.open(io.BytesIO(raw))
        fmt = probe.format
        if fmt not in ALLOWED_FORMATS:
            raise UserError(_("Only JPEG, PNG and WebP images are accepted (not %s).", fmt or _("this file type")))
        if probe.width * probe.height > MAX_PIXELS:
            raise UserError(_("The image has too many pixels (limit: %s megapixels).", MAX_PIXELS // 1000000))
        probe.verify()
        img = Image.open(io.BytesIO(raw))  # verify() leaves the first object unusable
        img.load()
    except UserError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        raise UserError(_("The uploaded file is not a valid JPEG, PNG or WebP image."))
    img = ImageOps.exif_transpose(img)
    max_w, max_h, out_fmt = IMAGE_LIMITS[kind]
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    out = io.BytesIO()
    if out_fmt == "PNG":
        img.convert("RGBA").save(out, "PNG", optimize=True)
        return out.getvalue(), "image/png"
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if kind == "logo" and has_alpha:
        img.convert("RGBA").save(out, "WEBP", quality=90, method=4)
    else:
        img.convert("RGB").save(out, "WEBP", quality=80, method=4)
    return out.getvalue(), "image/webp"
