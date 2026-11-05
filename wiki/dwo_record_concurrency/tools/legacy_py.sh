#!/bin/zsh
# usage: legacy_py.sh <NN> : python side shared by the legacy versions 12..15 (run inside the module dir)
v=$1
python3 - $v <<'EOF'
import sys
v=int(sys.argv[1])
def edit(p, fn):
    s=open(p).read(); open(p,'w').write(fn(s))
edit('__manifest__.py', lambda s: s.replace('"version": "16.0.1.1.0"', f'"version": "{v}.0.1.1.0"'))
open('models/__init__.py','w').write("from . import dwo_model_concurrency\nfrom . import base\nfrom . import dwo_record_presence\n")
open('__init__.py','w').write("from . import models\nfrom . import controllers\n")
open('controllers/__init__.py','w').write("from . import main\n")
open('controllers/main.py','w').write('''from odoo.http import request
from odoo.addons.bus.controllers.main import BusController

from ..models.dwo_record_presence import dwo_channel_allowed


class DwoBusController(BusController):

    def poll(self, channels, last, options=None):
        """Presence channels are plain strings chosen by the client: only let a user listen to the records
        he is allowed to read. (The route of the parent method is kept.)"""
        channels = [channel for channel in channels if dwo_channel_allowed(request.env, channel)]
        return super(DwoBusController, self).poll(channels, last, options)
''')
open('models/dwo_record_presence.py','w').write('''from odoo import api, models

CHANNEL_PREFIX = 'dwo_record_presence'


def dwo_channel_allowed(env, channel):
    """True unless ``channel`` is a presence channel of a record the user cannot read."""
    if not isinstance(channel, str) or not channel.startswith(CHANNEL_PREFIX + ':'):
        return True
    try:
        _prefix, model, res_id = channel.split(':', 2)
        record = env[model].browse(int(res_id)).exists()
        if not record:
            return False
        record.check_access_rights('read')
        record.check_access_rule('read')
        return True
    except Exception:  # noqa: BLE001 - malformed or unknown channel: refuse it
        return False


class RecordPresence(models.AbstractModel):
    _name = "dwo.record.presence"
    _description = "Record Presence Publisher"

    @api.model
    def publish_presence(self, model, res_id, state='stale', fields=None):
        """Publish a payload-less ping: who changed which fields of which record."""
        user = self.env.user
        message = {
            "model": model,
            "res_id": res_id,
            "user_id": user.id,
            "user_name": user.name,
            "current_tab_id": self.env.context.get('current_tab_id'),
            "state": state,
            "fields": list(fields or []),
        }
        channel = "%s:%s:%s" % (CHANNEL_PREFIX, model, res_id)
        bus = self.env["bus.bus"]
        if hasattr(bus, '_sendone'):    # 15
            bus._sendone(channel, 'dwo_record_presence', message)
        else:                           # 12 .. 14: the notification type travels inside the message
            bus.sendone(channel, {'type': 'dwo_record_presence', 'payload': message})
''')
EOF
