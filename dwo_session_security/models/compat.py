# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""What changed between Odoo 17 and 20 in the session API (one place, so the rest of the module is the same)."""
from odoo import release

if release.version_info[0] >= 20:
    from odoo.http import Response
    from odoo.http.response import FutureResponse
    from odoo.http.session import SessionExpiredException, logout as _logout, session_store as _session_store

    def session_logout(session, keep_db=True):
        _logout(session, keep_db=keep_db)

    def get_store():
        return _session_store()
else:
    from odoo.http import FutureResponse, Response, SessionExpiredException, root

    def session_logout(session, keep_db=True):
        session.logout(keep_db=keep_db)

    def get_store():
        return root.session_store

__all__ = ["FutureResponse", "Response", "SessionExpiredException", "get_store", "session_logout"]
