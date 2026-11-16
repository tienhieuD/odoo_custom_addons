# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Calendar invitations (.ics, iCalendar) and contact cards (.vcf, vCard 2.1/3.0/4.0): the fields a reader needs,
as plain data. Values are text only (the viewer escapes them); photos and binary values are not kept."""
import quopri
import re

MAX_ITEMS = 500
MAX_LIST = 200
LINE = re.compile(r"^([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)?)((?:;[^:]*)?):(.*)$")


def _decode(content):
    if content[:3] == b"\xef\xbb\xbf":
        content = content[3:]
    for codec in ("utf-8", "cp1252"):
        try:
            return content.decode(codec)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", "replace")


def _lines(text):
    """Logical lines: folded lines (starting with a space or a tab) are joined; vCard 2.1 quoted-printable
    values that end with ``=`` go on with the next line."""
    out = []
    for raw in re.split(r"\r\n|\n|\r", text):
        if raw[:1] in (" ", "\t") and out:
            out[-1] += raw[1:]
        elif out and out[-1].endswith("=") and "QUOTED-PRINTABLE" in out[-1].split(":", 1)[0].upper():
            out[-1] = out[-1][:-1] + raw
        elif raw.strip():
            out.append(raw)
    return out


def _params(text):
    params = {}
    for item in text.split(";")[1:]:
        key, _, value = item.partition("=")
        if not _:
            params.setdefault("TYPE", []).append(key.strip().strip('"'))
        else:
            params.setdefault(key.strip().upper(), []).extend(v.strip().strip('"') for v in value.split(","))
    return params


def _unescape(value):
    return re.sub(r"\\([nN,;\\])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), value)


def _value(params, value):
    if "QUOTED-PRINTABLE" in [e.upper() for e in params.get("ENCODING", [])]:
        charset = (params.get("CHARSET") or ["utf-8"])[0]
        try:
            value = quopri.decodestring(value.encode("latin-1", "replace")).decode(charset, "replace")
        except LookupError:
            value = quopri.decodestring(value.encode("latin-1", "replace")).decode("utf-8", "replace")
    return value


def _items(text, kind):
    """``[(name, params, value)]`` per object of ``kind`` (VEVENT, VCARD...), plus the properties outside."""
    objects, top, current, depth = [], [], None, []
    for line in _lines(text):
        match = LINE.match(line)
        if not match:
            continue
        name, params, value = match.group(1).upper().split(".")[-1], _params(match.group(2)), match.group(3)
        if name == "BEGIN":
            depth.append(value.strip().upper())
            if value.strip().upper() == kind and len(objects) < MAX_ITEMS:
                current = []
            continue
        if name == "END":
            ended = depth.pop() if depth else ""
            if ended == kind and current is not None:
                objects.append(current)
                current = None
            continue
        if current is not None and depth and depth[-1] == kind:
            current.append((name, params, _value(params, value)))
        elif current is None:
            top.append((name, params, _value(params, value)))
    return objects, top


def _when(params, value):
    """``20261120T090000Z`` -> ``2026-11-20 09:00 UTC``; a TZID is shown as it is; a date stays a date."""
    value = value.strip()
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})?(Z)?)?$", value)
    if not m:
        return value
    out = "%s-%s-%s" % m.group(1, 2, 3)
    if m.group(4):
        out += " %s:%s" % m.group(4, 5)
        if m.group(7):
            out += " UTC"
        elif params.get("TZID"):
            out += " (%s)" % params["TZID"][0]
    return out


def _person(params, value):
    email = re.sub(r"^mailto:", "", value.strip(), flags=re.I)
    name = (params.get("CN") or [""])[0]
    return "%s <%s>" % (name, email) if name and email else (name or email)


def parse_ics(content):
    text = _decode(content)
    events, top = _items(text, "VEVENT")
    method = next((v.strip().upper() for n, _p, v in top if n == "METHOD"), "")
    out = []
    for props in events:
        event = {"summary": "", "start": "", "end": "", "location": "", "description": "", "organizer": "",
                 "status": "", "recurrence": "", "url": "", "attendees": []}
        for name, params, value in props:
            if name == "SUMMARY":
                event["summary"] = _unescape(value)
            elif name == "DTSTART":
                event["start"] = _when(params, value)
            elif name == "DTEND":
                event["end"] = _when(params, value)
            elif name == "LOCATION":
                event["location"] = _unescape(value)
            elif name == "DESCRIPTION":
                event["description"] = _unescape(value)[:20000]
            elif name == "ORGANIZER":
                event["organizer"] = _person(params, value)
            elif name == "STATUS":
                event["status"] = value.strip().upper()
            elif name == "RRULE":
                event["recurrence"] = value.strip()
            elif name == "URL":
                event["url"] = value.strip()
            elif name == "ATTENDEE" and len(event["attendees"]) < MAX_LIST:
                event["attendees"].append({"name": _person(params, value),
                                           "status": (params.get("PARTSTAT") or [""])[0].upper()})
        out.append(event)
    return {"kind": "calendar", "method": method, "events": out}


def parse_vcf(content):
    text = _decode(content)
    cards, _top = _items(text, "VCARD")
    out = []
    for props in cards:
        card = {"name": "", "organization": "", "title": "", "birthday": "", "note": "", "url": "",
                "emails": [], "phones": [], "addresses": []}
        structured = ""
        for name, params, value in props:
            kinds = ", ".join(t.lower() for t in params.get("TYPE", []) if t and t.upper() not in ("PREF", "INTERNET"))
            if name == "FN":
                card["name"] = _unescape(value)
            elif name == "N":
                structured = " ".join(p for p in (_unescape(x).strip() for x in re.split(r"(?<!\\);", value)[1::-1]) if p)
            elif name == "ORG":
                card["organization"] = ", ".join(p for p in (_unescape(x).strip() for x in re.split(r"(?<!\\);", value)) if p)
            elif name == "TITLE":
                card["title"] = _unescape(value)
            elif name == "BDAY":
                card["birthday"] = _when({}, value.replace("-", "")) if re.match(r"^\d{4}-?\d{2}-?\d{2}$", value.strip()) else value.strip()
            elif name == "NOTE":
                card["note"] = _unescape(value)[:5000]
            elif name == "URL":
                card["url"] = value.strip()
            elif name == "EMAIL" and len(card["emails"]) < MAX_LIST:
                card["emails"].append({"value": value.strip(), "type": kinds})
            elif name == "TEL" and len(card["phones"]) < MAX_LIST:
                card["phones"].append({"value": re.sub(r"^tel:", "", value.strip(), flags=re.I), "type": kinds})
            elif name == "ADR" and len(card["addresses"]) < MAX_LIST:
                parts = [_unescape(x).strip() for x in re.split(r"(?<!\\);", value)]
                card["addresses"].append({"value": ", ".join(p for p in parts if p), "type": kinds})
        card["name"] = card["name"] or structured
        out.append(card)
    return {"kind": "contacts", "contacts": out}
