# -*- coding: utf-8 -*-
"""Safe evaluation of "who" expressions such as ``record.manager_id.user_id``.

The text is never passed to ``eval``: it is split on ``or``, each part must be
a plain attribute chain starting with ``record`` or ``user``, and the chain is
walked with ``mapped``. The result is a set of ``res.users`` ids.
"""
import logging
import re

from odoo import _

_logger = logging.getLogger(__name__)

PART_RE = re.compile(r"^(record|user)(\.[a-z_][a-z0-9_]*)+$")
RELATIONAL = ("many2one", "many2many", "one2many")


def split_expression(text):
    return [part.strip() for part in re.split(r"\s+or\s+", (text or "").strip())]


def check_expression(env, model_name, text):
    """Return an error message, or an empty string when the expression is valid."""
    if not (text or "").strip():
        return _("Type an expression.")
    for part in split_expression(text):
        if not PART_RE.match(part):
            return _(
                '"%s" is not allowed. Use record.field.field or user.field.field, '
                'joined with "or". No calls, no brackets.', part)
        head, *path = part.split(".")
        model = model_name if head == "record" else "res.users"
        for index, name in enumerate(path):
            if model not in env:
                return _('Model "%s" does not exist.', model)
            field = env[model]._fields.get(name)
            if not field:
                return _('Field "%(field)s" does not exist on %(model)s.', field=name, model=model)
            if index == len(path) - 1:
                if field.type in RELATIONAL and field.comodel_name == "res.users":
                    continue
                if field.type == "integer":
                    continue
                return _('"%s" must end on a field that points to users.', part)
            if field.type not in RELATIONAL:
                return _('"%(field)s" is not a relation, nothing can follow it.', field=name)
            model = field.comodel_name
    return ""


def eval_expression(record, user, text):
    """Return the set of user ids an expression gives for ``record`` / ``user``."""
    for part in split_expression(text):
        if not PART_RE.match(part):
            continue
        head, *path = part.split(".")
        obj = record.sudo() if head == "record" else user.sudo()
        try:
            for name in path:
                obj = obj.mapped(name) if hasattr(obj, "mapped") else obj
                if isinstance(obj, list):
                    break
        except Exception:  # an expression must never crash a button
            _logger.warning("Approval expression %r failed on %s", part, record, exc_info=True)
            continue
        ids = _user_ids(obj)
        if ids:
            return ids
    return set()


def _user_ids(value):
    if hasattr(value, "ids") and getattr(value, "_name", "") == "res.users":
        return set(value.ids)
    if isinstance(value, list):
        return {int(v) for v in value if isinstance(v, int) and v > 0}
    return set()
