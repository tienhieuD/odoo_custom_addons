# -*- coding: utf-8 -*-


def post_init_hook(env):
    """The administrator can send without approval in the companies that exist at the installation
    (a new company gets the same default from the field)."""
    admin = env.ref("base.user_admin", raise_if_not_found=False)
    if not admin:
        return
    for company in env["res.company"].with_context(active_test=False).search([]):
        if not company.dwo_mail_exempt_user_ids:
            company.dwo_mail_exempt_user_ids = admin
