# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""A reference engine for the tests of the Core. Not an Odoo model and never loaded in production: the tests make
the registry lookup return it (``patch_sample_engine``). To write a real engine, copy ``dwo_attpreview_mail``."""
from unittest.mock import patch


class SampleEngine:
    _dwo_engine_code = "sample"
    _dwo_engine_label = "Sample (plain text)"
    _dwo_engine_extensions = ("txt", "sample")
    _dwo_engine_output = "text"
    _dwo_engine_priority = 100
    _dwo_engine_version = "1"
    _dwo_engine_max_size_mb = 0

    def _dwo_engine_notice(self, extension):
        return "Sample notice: this kind of file is only a sample." if extension == "sample" else False

    def _dwo_render(self, content, filename):
        return {"type": "text", "data": content.decode("utf-8", "replace")}


class BoxEngine:
    """A container: ``name=data;name=data``. Its result is JSON (own viewer); the files inside are its parts."""
    _dwo_engine_code = "box"
    _dwo_engine_label = "Sample container"
    _dwo_engine_extensions = ("box",)
    _dwo_engine_output = "json"
    _dwo_engine_priority = 100
    _dwo_engine_version = "1"
    _dwo_engine_max_size_mb = 0

    def _dwo_engine_notice(self, extension):
        return False

    @staticmethod
    def _items(content):
        return [i.split("=", 1) for i in content.decode().split(";") if "=" in i]

    def _dwo_render(self, content, filename):
        return {"type": "json", "data": {"files": [n for n, _d in self._items(content)], "html": "<script>x</script>"}}

    def _dwo_extract_part(self, content, filename, index):
        items = self._items(content)
        if index >= len(items):
            return None
        name, data = items[index]
        return name, data.replace("|", ";").encode()


SAMPLE = SampleEngine()
BOX = BoxEngine()


def patch_sample_engine(testcase, *extra):
    """Add the sample engine (and ``extra`` engines) to the engines the registry lookup returns, for the
    duration of one test."""
    Mixin = type(testcase.env["dwo.attpreview.engine"])
    original = Mixin._dwo_get_engines

    def _dwo_get_engines(self):
        engines = original(self) + [SAMPLE, *extra]
        return sorted(engines, key=lambda e: (e._dwo_engine_priority, e._dwo_engine_code))

    patcher = patch.object(Mixin, "_dwo_get_engines", _dwo_get_engines)
    patcher.start()
    testcase.addCleanup(patcher.stop)
    return SAMPLE
