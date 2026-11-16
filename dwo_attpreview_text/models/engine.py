# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import models
from odoo.exceptions import UserError
from odoo.addons.dwo_attpreview_core.tools import safe_xml

from .. import text_tools
from ..text_tools import TextError


class AttPreviewEngineText(models.AbstractModel):
    """Text and code files: raw text with line numbers and syntax colours, plus a preview (Markdown, HTML, notebook,
    log, diff, subtitles, PO) or a structure (JSON, XML, YAML, TOML, INI tree, Markdown outline) when the kind of file
    has one. The server decodes the bytes and does the work that needs it (XML tree with the safe parser of the core,
    HTML sanitized, notebooks); the viewer (``static/src/js/text_viewer.js``) does the rest in the browser."""

    _name = "dwo.attpreview.engine.text"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine: text and code"

    _dwo_engine_code = "text"
    _dwo_engine_label = "Text & code (MD, HTML, XML, JSON, YAML, LOG...)"
    _dwo_engine_extensions = text_tools.EXTENSIONS
    _dwo_engine_output = "json"
    # a generic reader: an engine made for one of these extensions (office for csv...) wins
    _dwo_engine_priority = 200
    _dwo_engine_version = "1"
    _dwo_engine_max_size_mb = 0  # the global limit of the core (Settings); the text shown is cut at 10 MB
    _dwo_engine_dialog_width = "wide"

    def _dwo_render(self, content, filename):
        ext, group, lang = text_tools.file_format(filename)
        truncated = len(content) > text_tools.MAX_TEXT_BYTES
        try:
            text, encoding = text_tools.decode_text(content[: text_tools.MAX_TEXT_BYTES], truncated=truncated)
        except TextError:
            raise UserError(self.env._(
                "This file is not text: it holds binary data (it may be another kind of file with a text "
                "extension). Download it to open it with the right program."))
        data = {
            "kind": "text", "format": group, "ext": ext, "lang": lang, "encoding": encoding,
            "eol": text_tools.line_endings(text[:1_000_000]), "size": len(content), "truncated": truncated,
            "text": text,
        }
        if truncated:
            # the structure of a cut file would be wrong: no tree, no HTML / notebook preview (the viewer keeps the
            # views that read line by line: log levels, diff, Markdown...)
            return {"type": "json", "data": data}
        if group == "html":
            if len(text) <= text_tools.MAX_HTML_PREVIEW:
                data["html"], data["blocked_images"] = text_tools.preview_html(text)
        elif group == "xml":
            try:
                data["xml"] = text_tools.xml_tree(safe_xml(content))
            except (UserError, ValueError):
                data["structure_error"] = self.env._("The XML is not well formed: no tree. The raw text is shown.")
        elif group == "notebook":
            try:
                data["notebook"] = text_tools.notebook(text)
            except (ValueError, TypeError, AttributeError):
                data["structure_error"] = self.env._("This is not a valid notebook (JSON): the raw text is shown.")
        return {"type": "json", "data": data}

    def _dwo_engine_notice(self, extension):
        if extension == "mdx":
            return self.env._("MDX is shown as Markdown: its components (JSX) are not run.")
        return False
