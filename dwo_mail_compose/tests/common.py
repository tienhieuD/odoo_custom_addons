# -*- coding: utf-8 -*-
"""Odoo 13 and 12 have no ``mail.tests.common``: the little that the tests need (a mail gateway that records
what would be sent, an administrator, an employee, a way to make users) is here."""
from contextlib import contextmanager
from unittest.mock import patch

from odoo import exceptions
from odoo.addons.base.models.ir_mail_server import IrMailServer
from odoo.addons.mail.models.mail_mail import MailMail
from odoo.tests import common


def mail_new_test_user(env, login=None, groups="base.group_user", name=None, email=None, **kwargs):
    group_ids = [(6, 0, [env.ref(g.strip()).id for g in groups.split(",")])] if groups else [(5, 0, 0)]
    values = {
        "name": name or login, "login": login, "email": email or "%s@example.com" % login,
        "groups_id": group_ids,
    }
    values.update(kwargs)
    return env["res.users"].with_context(no_reset_password=True, mail_create_nosubscribe=True).create(values)


class MailCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._mails = []
        cls._mails_args = []
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_admin.write({"notification_type": "inbox"})
        cls.company_admin = cls.user_admin.company_id
        cls.company_admin.write({"email": "company@example.com"})
        cls.alias_domain = "test.com"
        cls.alias_catchall = "catchall.test"
        cls.env["ir.config_parameter"].set_param("mail.catchall.domain", cls.alias_domain)
        cls.env["ir.config_parameter"].set_param("mail.catchall.alias", cls.alias_catchall)
        cls.user_employee = mail_new_test_user(
            cls.env, login="employee", groups="base.group_user", name="Ernest Employee",
            email="e.e@example.com", company_id=cls.company_admin.id, notification_type="inbox",
            signature="--\nErnest")
        cls.partner_employee = cls.user_employee.partner_id

    def _init_mail_mock(self):
        self._mails = []
        self._mails_args = []
        self._new_mails = self.env["mail.mail"].sudo()

    @contextmanager
    def mock_mail_gateway(self, mail_unlink_sent=False, sim_error=None):
        build_email_origin = IrMailServer.build_email
        mail_create_origin = MailMail.create
        mail_unlink_origin = MailMail.unlink
        self.mail_unlink_sent = mail_unlink_sent
        self._init_mail_mock()

        def _connect(model, *args, **kwargs):
            return None

        def _build_email(model, *args, **kwargs):
            self._mails.append(kwargs)
            self._mails_args.append(args)
            return build_email_origin(model, *args, **kwargs)

        def _send_email(model, message, *args, **kwargs):
            if "@" not in message["To"]:
                raise AssertionError(model.NO_VALID_RECIPIENT)
            return message["Message-Id"]

        def _mail_create(model, *args, **kwargs):
            res = mail_create_origin(model, *args, **kwargs)
            self._new_mails += res.sudo()
            return res

        def _mail_unlink(model, *args, **kwargs):
            if self.mail_unlink_sent:
                return mail_unlink_origin(model, *args, **kwargs)
            return True

        with patch.object(IrMailServer, "connect", autospec=True, wraps=IrMailServer, side_effect=_connect), \
                patch.object(IrMailServer, "build_email", autospec=True, wraps=IrMailServer, side_effect=_build_email), \
                patch.object(IrMailServer, "send_email", autospec=True, wraps=IrMailServer, side_effect=_send_email), \
                patch.object(MailMail, "create", autospec=True, wraps=MailMail, side_effect=_mail_create), \
                patch.object(MailMail, "unlink", autospec=True, wraps=MailMail, side_effect=_mail_unlink):
            yield
