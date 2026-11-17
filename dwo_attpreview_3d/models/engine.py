# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import io
import json
import zipfile

from odoo import models
from odoo.exceptions import UserError

MAX_3MF_UNPACKED = 512 * 1024 * 1024
MAX_3MF_ENTRIES = 20000
MESH_KINDS = ("stl", "obj", "ply")
SCENE_KINDS = ("glb", "gltf", "3mf", "fbx", "dae")
STEP_KINDS = ("step", "stp", "iges", "igs")


class AttPreview3DEngine(models.AbstractModel):
    """3D models (STL, OBJ, GLB/GLTF, 3MF, PLY, FBX, DAE) and CAD solids (STEP, IGES, Rhino 3DM), drawn in the browser by
    three.js in a sandboxed frame (STEP and IGES are meshed by Open CASCADE, 3DM read by rhino3dm, both WebAssembly).
    The server only checks that the file is what its extension says (and sane); it parses nothing but the JSON of a
    .gltf."""

    _name = "dwo.attpreview.engine.model3d"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview: 3D models"

    _dwo_engine_code = "model3d"
    _dwo_engine_label = "3D models (STL, OBJ, GLB, GLTF, 3MF, PLY, FBX, DAE, STEP, IGES, 3DM)"
    _dwo_engine_extensions = MESH_KINDS + SCENE_KINDS + STEP_KINDS + ("3dm",)
    _dwo_engine_output = "text"
    _dwo_engine_priority = 10
    _dwo_engine_size_groups = (
        ("model3d_mesh", MESH_KINDS, 50),
        ("model3d_scene", SCENE_KINDS, 50),
        ("model3d_step", STEP_KINDS, 25),
        ("model3d_rhino", ("3dm",), 50),
    )

    def _dwo_render(self, content, filename):
        kind = (filename or "").rsplit(".", 1)[-1].lower()
        if not content:
            raise UserError(self.env._("The file is empty."))
        check = getattr(self, "_dwo_check_" + kind, None)
        if check is None:
            raise UserError(self.env._("Unsupported file type."))
        check(content)
        return {"type": "text", "data": kind}

    def _dwo_bad(self, kind):
        return UserError(self.env._(
            "This is not a valid %s file (it may be damaged or saved in another format).", kind.upper()))

    @staticmethod
    def _dwo_head(content, size=2048):
        return content[:size].lstrip(b"\xef\xbb\xbf \t\r\n")

    def _dwo_check_stl(self, content):
        # binary: 80 byte header, a triangle count, 50 bytes per triangle; ASCII starts with "solid"
        if len(content) >= 84 and 84 + 50 * int.from_bytes(content[80:84], "little") == len(content):
            return
        head = self._dwo_head(content)
        if head[:5].lower() == b"solid" and b"\0" not in content[:4096]:
            return
        raise self._dwo_bad("stl")

    def _dwo_check_obj(self, content):
        if b"\0" in content[:4096] or b"\nv " not in b"\n" + content[:200000].replace(b"\r", b""):
            raise self._dwo_bad("obj")

    def _dwo_check_ply(self, content):
        if self._dwo_head(content)[:3] != b"ply":
            raise self._dwo_bad("ply")

    def _dwo_check_glb(self, content):
        if content[:4] != b"glTF" or len(content) < 20:
            raise self._dwo_bad("glb")

    def _dwo_check_gltf(self, content):
        try:
            doc = json.loads(content.decode("utf-8-sig"))
        except (ValueError, UnicodeDecodeError):
            raise self._dwo_bad("gltf")
        if not isinstance(doc, dict) or "asset" not in doc:
            raise self._dwo_bad("gltf")
        for item in list(doc.get("buffers", [])) + list(doc.get("images", [])):
            uri = item.get("uri") if isinstance(item, dict) else None
            if uri and not uri.startswith("data:"):
                raise UserError(self.env._(
                    "This glTF file refers to separate files (%s). Use a .glb file, or a .gltf with the data inside.",
                    str(uri)[:80]))

    def _dwo_check_step(self, content):
        head = self._dwo_head(content, 4096)
        if not head.startswith(b"ISO-10303-21") or b"FILE_SCHEMA" not in content[:65536]:
            raise self._dwo_bad("step")

    _dwo_check_stp = _dwo_check_step

    def _dwo_check_iges(self, content):
        # fixed 80-column records; the first one is the Start section, with S in column 73
        first = content[:81].split(b"\n")[0].rstrip(b"\r")
        if len(first) < 73 or first[72:73] != b"S" or b"\0" in content[:2048]:
            raise self._dwo_bad("iges")

    _dwo_check_igs = _dwo_check_iges

    def _dwo_check_3dm(self, content):
        if not content.startswith(b"3D Geometry File Format"):
            raise self._dwo_bad("3dm")

    def _dwo_check_fbx(self, content):
        if not (content.startswith(b"Kaydara FBX Binary") or self._dwo_head(content)[:1] == b";"
                or b"FBXHeaderExtension" in content[:2000]):
            raise self._dwo_bad("fbx")

    def _dwo_check_dae(self, content):
        if b"<COLLADA" not in content[:4096] and b"<collada" not in content[:4096]:
            raise self._dwo_bad("dae")

    def _dwo_check_3mf(self, content):
        if not content.startswith(b"PK"):
            raise self._dwo_bad("3mf")
        try:
            infos = zipfile.ZipFile(io.BytesIO(content)).infolist()
        except (zipfile.BadZipFile, ValueError, OSError):
            raise UserError(self.env._("The file is damaged and cannot be opened."))
        if len(infos) > MAX_3MF_ENTRIES or sum(i.file_size for i in infos) > MAX_3MF_UNPACKED:
            raise UserError(self.env._("This file is too large once unpacked to be previewed."))
        if not any(i.filename.lower().endswith(".model") for i in infos):
            raise self._dwo_bad("3mf")
