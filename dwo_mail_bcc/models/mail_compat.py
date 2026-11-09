# -*- coding: utf-8 -*-
"""Mail address helpers that exist in some Odoo versions only."""
from email.utils import getaddresses

from odoo.tools import mail as mail_tools


def email_normalize(text):
    """The lower-cased address of a text holding exactly one address, else False.

    Odoo 12 has no ``email_normalize``.
    """
    emails = mail_tools.email_split(text or "")
    if len(emails) != 1:
        return False
    local_part, at, domain = emails[0].rpartition("@")
    return local_part.lower() + at + domain.lower()


def _split_tuples(text):
    """(name, address) pairs; Odoo 12 has no ``email_split_tuples``."""
    return [(name, address) for name, address in getaddresses([text]) if address and "@" in address]


def split_and_format_normalize(text):
    """'Name <A@x.com>, b@y.com' -> ['Name <a@x.com>', 'b@y.com'] (the addresses lower-cased).

    ``email_split_and_format_normalize`` exists from Odoo 18; before it, the same is built from
    ``email_split_tuples``.
    """
    native = getattr(mail_tools, "email_split_and_format_normalize", None)
    if native:
        return native(text)
    result = []
    # Odoo 18 reads ';' as a separator too
    # older versions find no address at all in a text with an empty item (a trailing comma)
    text = (text or "").replace(";", ",").strip(" ,")
    for name, address in _split_tuples(text):
        result.append(mail_tools.formataddr((name, email_normalize(address) or address)))
    return result


def normalize_all(values):
    """The normalized addresses of a text or of a list of texts ('Name <a@x.com>')."""
    if isinstance(values, str):
        values = [values]
    result = []
    for value in values or []:
        for formatted in split_and_format_normalize(value):
            normalized = email_normalize(formatted)
            if normalized and normalized not in result:
                result.append(normalized)
    return result
