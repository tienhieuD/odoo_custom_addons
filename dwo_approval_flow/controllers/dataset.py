# -*- coding: utf-8 -*-
"""A button of the screen that calls a method an approval arrow also calls goes through the arrow.

Only the calls of the web client are checked (``/web/dataset/call_kw`` and ``call_button``): code, scheduled actions and
external RPC are not blocked. The check is one lookup of a set, then nothing for every other method.
"""
from odoo import http
from odoo.addons.web.controllers.dataset import DataSet
from odoo.http import request


class DwoDataSet(DataSet):

    def _dwo_guard(self, model, method, args):
        """``None`` when the call is not protected, else ``(ids the method may run on, result of the arrow or None)``."""
        ids = args[0] if args and isinstance(args[0], (list, tuple)) else None
        if not ids or not all(isinstance(i, int) for i in ids):
            return None
        flow = request.env["dwo.approval.flow"]
        if (model, method) not in flow._guard_methods():
            return None
        return flow._guard_rpc(model, method, list(ids))

    def _dwo_run(self, call, model, method, args):
        guarded = self._dwo_guard(model, method, args)
        if guarded is None:
            return call(args)
        free_ids, result = guarded
        real = call([free_ids] + list(args[1:])) if free_ids else None
        return result if result is not None else real

    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type="json", auth="user",
                readonly=DataSet._call_kw_readonly)
    def call_kw(self, model, method, args, kwargs, path=None):
        return self._dwo_run(lambda a: super(DwoDataSet, self).call_kw(model, method, a, kwargs, path), model, method, args)

    @http.route(['/web/dataset/call_button', '/web/dataset/call_button/<path:path>'], type="json", auth="user",
                readonly=DataSet._call_kw_readonly)
    def call_button(self, model, method, args, kwargs, path=None):
        return self._dwo_run(lambda a: super(DwoDataSet, self).call_button(model, method, a, kwargs, path), model, method, args)
