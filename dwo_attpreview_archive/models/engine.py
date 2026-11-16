# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import models
from odoo.exceptions import UserError

from ..parsers import ArchiveError, extract_member, list_archive

MIN_EXTRACT_MB = 100  # a file inside an archive may be downloaded up to this size (or the preview limit if larger)


class AttPreviewEngineArchive(models.AbstractModel):
    _name = "dwo.attpreview.engine.archive"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine: archives"

    _dwo_engine_code = "archive"
    _dwo_engine_label = "Archives (ZIP, RAR, 7Z, TAR)"
    _dwo_engine_extensions = ("zip", "rar", "7z", "tar", "tgz", "gz", "bz2", "tbz2", "tbz", "xz", "txz")
    _dwo_engine_output = "json"
    _dwo_engine_priority = 10
    _dwo_engine_version = "1"
    _dwo_engine_dialog_width = "medium"

    def _dwo_render(self, content, filename):
        try:
            data = list_archive(content, filename)
        except ArchiveError as e:
            raise UserError(self._dwo_message(e))
        data.update(kind="archive", extract_hint=self._dwo_extract_hint(data["format"]))
        return {"type": "json", "data": data}

    def _dwo_extract_part(self, content, filename, index):
        limit = max(self.env["dwo.attpreview.cache"]._param("max_file_size_mb", 20), MIN_EXTRACT_MB) * 1024 * 1024
        try:
            return extract_member(content, filename, index, limit)
        except ArchiveError as e:
            raise UserError(self._dwo_message(e))

    @staticmethod
    def _dwo_message(error):
        return ("%s %s" % (error, error.hint)).strip() if getattr(error, "hint", "") else str(error)

    def _dwo_extract_hint(self, kind):
        """Why the files of this archive cannot be opened on this server (empty: they can)."""
        if kind != "rar":
            return ""
        from ..thirdparty import rarfile
        try:
            rarfile.tool_setup()
        except rarfile.RarCannotExec:
            return self.env._("Compressed files inside RAR archives open only when unrar is installed on the server "
                              "(Debian/Ubuntu: apt install unrar). The list of files is always shown.")
        return ""
