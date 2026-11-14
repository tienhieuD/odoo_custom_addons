# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers.discuss import DiscussController


class DwoThreadController(DiscussController):

    @http.route()
    def mail_thread_messages(self, thread_model, thread_id, *args, dwo_filter_id=None, dwo_search=None, **kwargs):
        """The chatter asks for the messages of one chip: ``mail.message._message_fetch`` reads them in the context."""
        extra = {key: value for key, value in (("dwo_filter_id", dwo_filter_id), ("dwo_search", dwo_search)) if value}
        if extra:
            # Odoo 15 has no request.update_context (16): the setter of the context makes the environment again
            request.context = dict(request.context, **extra)
        return super().mail_thread_messages(thread_model, thread_id, *args, **kwargs)
