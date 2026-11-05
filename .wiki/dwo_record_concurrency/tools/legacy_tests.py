"""usage: legacy_tests.py <NN>  (python tests of the legacy versions 12..15, run from the module dir)"""
import re, sys
p = 'tests/test_concurrency.py'
s = open(p).read()
a = s.index("    def _capture_bus(self):")
b = s.index("    def test_ping_has_names_only")
s = s[:a] + '''    def _capture_bus(self):
        sent = []
        bus_cls = type(self.env['bus.bus'])
        if hasattr(bus_cls, '_sendone'):
            def _sendone(this, target, notification_type, message):
                sent.append((target, notification_type, message))
            return sent, patch.object(bus_cls, '_sendone', _sendone)

        def sendone(this, channel, message):    # 12 .. 14: the type travels inside the message
            sent.append((channel, message.get('type'), message.get('payload')))
        return sent, patch.object(bus_cls, 'sendone', sendone)

''' + s[b:]
s = s.replace("from odoo.tests import TransactionCase, tagged, new_test_user\n",
              "from odoo.tests import TransactionCase, tagged\nfrom odoo.addons.dwo_record_concurrency.models.dwo_record_presence import dwo_channel_allowed\n" + ("from odoo.tests.common import new_test_user\n" if int(sys.argv[1]) >= 13 else "") )
# the websocket based tests
a = s.index("    def test_presence_channel_follows_read_access")
b = s.index("    def test_only_administrators_edit_the_configuration")
s = s[:a] + '''    def test_presence_channel_follows_read_access(self):
        env = self.env
        channel = 'dwo_record_presence:res.partner:%s' % self.partner.id
        self.assertTrue(dwo_channel_allowed(env, channel))
        self.assertTrue(dwo_channel_allowed(env, 'some_other_channel'))
        portal = new_test_user(env, login='dwo_portal', groups='base.group_portal')
        # a portal user cannot read the records of an internal model
        self.assertFalse(dwo_channel_allowed(env(user=portal.id), 'dwo_record_presence:ir.cron:1'))
        self.assertFalse(dwo_channel_allowed(env, 'dwo_record_presence:garbage'))

''' + s[b:]
a = s.index("    def test_bus_channel_list_drops_forbidden_presence_channels")
b = s.index("    def test_presence_ping_never_contains_values")
s = s[:a] + s[b:]
open(p, 'w').write(s)
