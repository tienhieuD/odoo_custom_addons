# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import re
from email import policy
from email.parser import BytesParser

from odoo import models
from odoo.addons.dwo_attpreview_core.tools import esc, table_html

REMOTE_SRC = re.compile(r"""\s(src|background|srcset)\s*=\s*(["'])\s*(?:https?:)?//[^"']*\2""", re.I)
CID_SRC = re.compile(r"""src\s*=\s*(["'])cid:([^"']+)\1""", re.I)
CSS_URL = re.compile(r"""url\(\s*['"]?\s*(?:https?:)?//[^)]*\)""", re.I)


class AttPreviewEngineMail(models.AbstractModel):
    _name = "dwo.attpreview.engine.mail"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine: mail"

    _dwo_engine_code = "mail"
    _dwo_engine_label = "Email, calendar, vCard"
    _dwo_engine_extensions = ("eml", "ics", "vcf")
    _dwo_engine_output = "html"
    _dwo_engine_priority = 10

    def _dwo_render(self, content, filename):
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "eml":
            return {"type": "html", "data": self._eml(content)}
        text = content.decode("utf-8", "replace")
        unfolded = re.sub(r"\r?\n[ \t]", "", text)
        rows = []
        for line in unfolded.splitlines():
            if ":" in line and not line.startswith(("BEGIN", "END")):
                key, _, val = line.partition(":")
                rows.append([key.split(";")[0], val.replace("\\n", "\n").replace("\\,", ",")])
        return {"type": "html", "data": table_html(rows)}

    def _eml(self, content):
        msg = BytesParser(policy=policy.default).parsebytes(content)
        head = "".join(
            "<tr><th align='left'>%s</th><td>%s</td></tr>" % (esc(h), esc(str(msg.get(h, ""))))
            for h in ("From", "To", "Cc", "Date", "Subject") if msg.get(h))
        cids = {}
        atts = []
        for part in msg.walk():
            if part.is_multipart():
                continue
            cid = (part.get("Content-ID") or "").strip("<>")
            ctype = part.get_content_type()
            if cid and ctype.startswith("image/"):
                data = part.get_payload(decode=True) or b""
                if len(data) < 5 * 1024 * 1024:
                    cids[cid] = "data:%s;base64,%s" % (ctype, base64.b64encode(data).decode())
            fn = part.get_filename()
            if fn:
                atts.append((fn, len(part.get_payload(decode=True) or b"")))
        body_part = msg.get_body(preferencelist=("html", "plain"))
        body = ""
        if body_part is not None:
            raw = body_part.get_content()
            if body_part.get_content_type() == "text/html":
                body = CID_SRC.sub(lambda m: 'src="%s"' % cids.get(m.group(2), ""), raw)
                body = REMOTE_SRC.sub("", body)
                body = CSS_URL.sub("none", body)
            else:
                body = "<pre style='white-space:pre-wrap'>%s</pre>" % esc(raw)
        att_html = ""
        if atts:
            att_html = "<hr/><b>Attachments</b><ul>%s</ul>" % "".join(
                "<li>%s (%d KB)</li>" % (esc(n), s // 1024) for n, s in atts)
        return "<table style='font-family:sans-serif;font-size:13px'>%s</table><hr/>%s%s" % (head, body, att_html)
