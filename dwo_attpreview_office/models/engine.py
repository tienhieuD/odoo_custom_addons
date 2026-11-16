# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import io
import zipfile

from odoo import models
from odoo.exceptions import UserError

# Same ceilings as the viewer library (resourceLimits of @silurus/ooxml): 128 MiB per part, 256 MiB in total.
MAX_ENTRY_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_ENTRIES = 20000

# Delimited text, shown as a sheet where every cell stays text (no type guessing)
TEXT_KINDS = ("csv", "tsv")

# the part that every real file of that type has
MAIN_PART = {
    "xlsx": "xl/workbook.xml",
    "docx": "word/document.xml",
    "pptx": "ppt/presentation.xml",
}

# Macro-enabled and template variants of the same three formats (#70): same zip layout and same main part, only the
# content type in [Content_Types].xml differs (and a vbaProject.bin part for the macro ones). The viewer draws them
# as the base type; macros are never run (the library does not read vbaProject.bin, and the viewer runs no script of
# the file). Checked one by one with the tours (tests/test_engine.py, test_4x).
VARIANTS = {
    "xlsm": "xlsx", "xltx": "xlsx", "xltm": "xlsx",
    "docm": "docx", "dotx": "docx", "dotm": "docx",
    "pptm": "pptx", "ppsx": "pptx", "ppsm": "pptx", "potx": "pptx", "potm": "pptx",
}


# Old binary formats (Word 97-2003, Excel 97-2003, PowerPoint 97-2003): a Compound File Binary (OLE) container,
# opened in the browser by the optional silurus legacy add-on (static/lib/silurus/{doc,xls,ppt}.mjs).
LEGACY_KINDS = ("doc", "xls", "ppt")
CFB_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
CFB_MIN_BYTES = 512  # one sector: the header alone is 512 bytes


class AttPreviewEngineOffice(models.AbstractModel):
    """xlsx, docx and pptx (with their macro-enabled and template variants, and the old doc, xls, ppt, with a warning) are drawn in the browser by the bundled silurus viewer (static/lib/silurus), inside
    a sandboxed iframe. The server only checks that the file is a sane Office zip (and not too large once
    unpacked), then hands the file type to the viewer; the bytes come from /dwo_attpreview_office/file/<id>."""

    _name = "dwo.attpreview.engine.office"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine: xlsx, docx, pptx (and doc, xls, ppt)"

    _dwo_engine_code = "office"
    _dwo_engine_label = "XLSX, DOCX, PPTX, DOC, XLS, PPT, CSV, TSV"
    _dwo_engine_extensions = (
        "xlsx", "docx", "pptx", "doc", "xls", "ppt", "csv", "tsv",
    ) + tuple(VARIANTS)
    _dwo_engine_output = "text"
    _dwo_engine_priority = 10

    def _dwo_engine_notice(self, extension):
        if extension in LEGACY_KINDS:
            return self.env._(
                "Legacy format (.doc/.xls/.ppt): support is limited. The file may show incorrectly or fail to open. "
                "Download it to see it in full.")
        return False

    def _dwo_check_legacy(self, content, kind):
        """An old binary file: a Compound File (OLE) container. Only the signature is checked here; the content is
        parsed in the browser (WebAssembly, in the sandboxed iframe), never in the Odoo process. The size limit is
        the one of the Core, applied before this check."""
        if not content:
            raise UserError(self.env._("The file is empty."))
        if len(content) < CFB_MIN_BYTES or not content.startswith(CFB_SIGNATURE):
            raise UserError(self.env._(
                "This is not a valid .%s file (it may be damaged or saved in another format).", kind))

    def _dwo_check_text(self, content, kind):
        """csv / tsv: not empty and not binary (a NUL byte means it is not text; UTF-16 files have them too). The
        text is parsed in the browser; the size limit is the one of the Core."""
        if not content:
            raise UserError(self.env._("The file is empty."))
        if b"\0" in content:
            raise UserError(self.env._(
                "This is not a valid .%s file (it is binary, or not saved as UTF-8 text).", kind))

    def _dwo_check_zip(self, content, kind, base=None):
        """kind: the extension of the file (for the messages); base: xlsx/docx/pptx, the type it is checked as."""
        base = base or kind
        if not content:
            raise UserError(self.env._("The file is empty."))
        if not content.startswith(b"PK"):
            raise UserError(self.env._(
                "This is not a valid %s file (it may be damaged, encrypted or in an older format).", kind.upper()))
        try:
            zf = zipfile.ZipFile(io.BytesIO(content))
            infos = zf.infolist()
        except (zipfile.BadZipFile, ValueError, OSError):
            raise UserError(self.env._("The file is damaged and cannot be opened."))
        if len(infos) > MAX_ENTRIES:
            raise UserError(self.env._("The file contains too many parts to be previewed."))
        total = 0
        for info in infos:
            if info.file_size > MAX_ENTRY_BYTES:
                raise UserError(self.env._("A part of this file is too large once unpacked to be previewed."))
            total += info.file_size
        if total > MAX_TOTAL_BYTES:
            raise UserError(self.env._("This file is too large once unpacked to be previewed."))
        if MAIN_PART[base] not in {i.filename for i in infos}:
            raise UserError(self.env._("This is not a valid %s file (the main part is missing).", kind.upper()))

    def _dwo_render(self, content, filename):
        kind = (filename or "").rsplit(".", 1)[-1].lower()
        if kind in LEGACY_KINDS:
            self._dwo_check_legacy(content, kind)
        elif kind in TEXT_KINDS:
            self._dwo_check_text(content, kind)
        elif kind in MAIN_PART:
            self._dwo_check_zip(content, kind)
        elif kind in VARIANTS:
            self._dwo_check_zip(content, kind, VARIANTS[kind])
            # the viewer only needs the base type
            kind = VARIANTS[kind]
        else:
            raise UserError(self.env._("Unsupported file type."))
        return {"type": "text", "data": kind}
