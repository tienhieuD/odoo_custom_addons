# -*- coding: utf-8 -*-
"""Mail address helpers that exist in some Odoo versions only."""
from odoo.tools import mail as mail_tools


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
    for name, address in mail_tools.email_split_tuples((text or "").replace(";", ",")):
        result.append(mail_tools.formataddr((name, mail_tools.email_normalize(address) or address)))
    return result


def normalize_all(values):
    """The normalized addresses of a text or of a list of texts ('Name <a@x.com>')."""
    if isinstance(values, str):
        values = [values]
    result = []
    for value in values or []:
        for formatted in split_and_format_normalize(value):
            normalized = mail_tools.email_normalize(formatted)
            if normalized and normalized not in result:
                result.append(normalized)
    return result
