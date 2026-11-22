# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.home import Home

SETTINGS_URL = "/odoo/settings#dwo_login_themes"
# the places a visitor lands by default: after a login without a given page, the settings of the login themes open
DEFAULT_LANDING = (None, "", "/", "/odoo", "/odoo?", "/odoo/", "/web", "/web?")


class DemoHome(Home):

    def _login_redirect(self, uid, redirect=None):
        if redirect in DEFAULT_LANDING:
            return SETTINGS_URL
        return super()._login_redirect(uid, redirect=redirect)
