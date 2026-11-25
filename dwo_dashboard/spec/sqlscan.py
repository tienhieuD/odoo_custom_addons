# -*- coding: utf-8 -*-
"""A small scanner for the query of a SQL dataset. Pure Python, no database.

It does not make a query safe (the database role and the plan check do that, see engine/sql.py); it makes it ONE statement that
cannot get out of the parentheses it is wrapped in: a single ``SELECT`` or ``WITH ... SELECT``, no ``;`` outside a literal or a
comment, balanced parentheses, closed strings and comments, and every ``%`` either a ``%%`` or a ``%(name)s`` placeholder.
It knows the lexical forms that can hide a character from a naive search: ``'...'`` with ``''``, ``E'...'`` with backslashes,
``"identifiers"``, ``-- line`` and nested ``/* block */`` comments, and ``$tag$ dollar quotes $tag$``."""
import re

PLACEHOLDER = re.compile(r"%\((\w+)\)s")
FIRST_WORDS = ("select", "with")
# calls that can read files, run other SQL, reach other servers or change the session: never in a dataset (the database role is
# what protects the server; this keeps the obvious doors shut and gives a clear message)
DENIED_CALLS = re.compile(r'"?\b(set_config|current_setting|query_to_xml\w*|table_to_xml\w*|cursor_to_xml|database_to_xml|schema_to_xml|'
                          r'pg_\w+|lo_\w+|dblink\w*|txid_\w+|nextval|setval|currval|xmlparse)\b"?\s*\(', re.I)  # a quoted name too


def scan(query):
    """Returns ``(errors, placeholders)``: the problems found (strings), and the names used as ``%(name)s``."""
    errors, names = [], []
    i, n, depth = 0, len(query), 0
    first = None
    while i < n:
        c = query[i]
        if c == "'":
            escape = i > 0 and query[i - 1] in "eE" and (i < 2 or not (query[i - 2].isalnum() or query[i - 2] == "_"))
            i = _string(query, i, escape)
            if i < 0:
                return ["a string is never closed"], names
            first = first or "'"
            continue
        if c == '"':
            end = query.find('"', i + 1)
            while end != -1 and query[end + 1:end + 2] == '"':
                end = query.find('"', end + 2)
            if end == -1:
                return ["a quoted name is never closed"], names
            i = end + 1
            first = first or '"'
            continue
        if query.startswith("--", i):
            end = query.find("\n", i)
            i = n if end == -1 else end + 1
            continue
        if query.startswith("/*", i):
            i = _block(query, i)
            if i < 0:
                return ["a comment is never closed"], names
            continue
        if c == "$":
            m = re.match(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$", query[i:])
            if m:
                end = query.find(m.group(0), i + len(m.group(0)))
                if end == -1:
                    return ["a dollar-quoted string is never closed"], names
                i = end + len(m.group(0))
                first = first or "$"
                continue
        if c == ";":
            errors.append("a query is one statement: remove the ';'")
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth < 0:
                return ["a ')' closes nothing"], names
        elif first is None and not c.isspace():
            word = re.match(r"[A-Za-z]+", query[i:])
            first = word.group(0).lower() if word else c
            if first not in FIRST_WORDS:
                errors.append("a query starts with SELECT or WITH, not %r" % first)
            i += len(word.group(0)) if word else 1
            continue
        i += 1
    for call in dict.fromkeys(m.group(1).lower() for m in DENIED_CALLS.finditer(query)):
        errors.append("the function %s() is not allowed in a dataset" % call)
    # the driver substitutes parameters in the WHOLE text, literals and comments included: every % must be %% or %(name)s
    plain = PLACEHOLDER.sub("", query.replace("%%", ""))
    if "%" in plain:
        errors.append("a lone '%' (write %% for a percent sign, %(name)s for a parameter)")
    names = PLACEHOLDER.findall(query.replace("%%", ""))
    if depth:
        errors.append("parentheses are not balanced")
    if first is None:
        errors.append("the query is empty")
    return list(dict.fromkeys(errors)), names


def _string(query, i, escape):
    """The index after the string that opens at ``i`` (``''`` is a quote; with ``E'`` a backslash escapes), or -1."""
    j = i + 1
    while j < len(query):
        c = query[j]
        if escape and c == "\\":
            j += 2
            continue
        if c == "'":
            if query[j + 1:j + 2] == "'":
                j += 2
                continue
            return j + 1
        j += 1
    return -1


def _block(query, i):
    """The index after the block comment at ``i``; they nest in PostgreSQL. -1 if it is never closed."""
    depth, j = 0, i
    while j < len(query):
        if query.startswith("/*", j):
            depth += 1
            j += 2
        elif query.startswith("*/", j):
            depth -= 1
            j += 2
            if depth == 0:
                return j
        else:
            j += 1
    return -1
