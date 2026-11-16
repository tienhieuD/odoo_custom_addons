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


SAMPLE = SampleEngine()


def patch_sample_engine(testcase):
    """Add the sample engine to the engines the registry lookup returns, for the duration of one test."""
    Mixin = type(testcase.env["dwo.attpreview.engine"])
    original = Mixin._dwo_get_engines

    def _dwo_get_engines(self):
        engines = original(self) + [SAMPLE]
        return sorted(engines, key=lambda e: (e._dwo_engine_priority, e._dwo_engine_code))

    patcher = patch.object(Mixin, "_dwo_get_engines", _dwo_get_engines)
    patcher.start()
    testcase.addCleanup(patcher.stop)
    return SAMPLE
