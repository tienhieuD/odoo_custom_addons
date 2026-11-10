# -*- coding: utf-8 -*-
"""Odoo 13 and 12: little helpers that later versions have in ``odoo.tools``."""
import re

from lxml import html as lxml_html

_MEDIA = ("img", "video", "audio", "iframe", "embed", "object", "svg", "canvas", "hr", "table")


def is_html_empty(html_content):
    """True when an HTML has no text and no picture or other content (odoo.tools.is_html_empty, Odoo 15)."""
    if not html_content:
        return True
    text = str(html_content)
    if not text.strip():
        return True
    try:
        root = lxml_html.fragment_fromstring(text, create_parent="div")
    except Exception:
        return not re.sub(r"<[^>]*>|&nbsp;|\s+", "", text)
    if any(root.iter(*_MEDIA)):
        return False
    return not "".join(root.itertext()).replace("\xa0", "").strip()
