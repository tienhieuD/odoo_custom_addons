# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers.thread import ThreadController


class DwoThreadController(ThreadController):

    @http.route()
    def mail_thread_messages(self, thread_model, thread_id, *args, dwo_filter_id=None, **kwargs):
        """The chatter asks for the messages of one chip: ``mail.message._message_fetch`` reads it in the context."""
        if dwo_filter_id:
            request.update_context(dwo_filter_id=dwo_filter_id)
        return super().mail_thread_messages(thread_model, thread_id, *args, **kwargs)
