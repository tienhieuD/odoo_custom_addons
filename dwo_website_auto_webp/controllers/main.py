import logging

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Binary

_logger = logging.getLogger(__name__)


class WebpBinary(Binary):

    @http.route()
    def content_image(self, *args, **kwargs):
        """
        Wrap /web/image: let the standard controller build the (resized) image response,
        then convert it to WebP for browsers that accept it. Any failure falls back to the
        original response, so images are never broken by this module.
        """
        response = super(WebpBinary, self).content_image(*args, **kwargs)
        try:
            return request.env['dwo.webp.helper']._webp_process_response(response, kwargs)
        except Exception:
            _logger.warning('dwo_website_auto_webp: unexpected error, fallback to original', exc_info=True)
            return response
