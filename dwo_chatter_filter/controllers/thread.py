# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers.discuss import DiscussController


class DwoThreadController(DiscussController):

    @http.route()
    def mail_thread_messages(self, thread_model, thread_id, *args, dwo_category=None, **kwargs):
        """The chatter asks for one kind of message: ``mail.message._message_fetch`` reads it in the context."""
        if dwo_category:
            request.update_context(dwo_category=dwo_category)
        return super().mail_thread_messages(thread_model, thread_id, *args, **kwargs)
