# Changelog

## 19.0.1.0.0 - 2026-11-18 (issue #92)

First version. One module, all features.

**What it does**
- Lock screen with a 4 or 6 digit PIN after an idle time; the PIN is chosen in Preferences, tab Security (wizard `dwo.pin.wizard`, asks the account password).
- Server side time limits: idle sign-out and maximum duration, per session; exempt group `Session security: exempt from time limits`.
- Warning toast N minutes before the end of the session (default 30, on/off), with an Extend button (on/off, minutes and number of extensions set by the administrator).
- Closing the browser ends the session: browser-session cookie (no Expires, no Max-Age) and a heartbeat per tab watched by the server.
- Expiry dialog in the web client, then the login page, then back to the same screen (`/dwo/session/relogin?r=<path>`; only internal paths are accepted).
- Session approval (off by default): group `Session security: sign-in needs approval`; the user waits on `/dwo/session/waiting`; approvers (administrators, group `Session security: approver`) are told by toast, email and/or activity; approve or reject on the request, in the toast, or on the activity. Administrators are never asked.
- Forgot the PIN, each way on/off: sign in again (password or login page for SSO/2FA, then a new PIN), ask an administrator (request + approval), code by email (6 digits, 10 minutes, 3 per hour), temporary PIN from an administrator (user form).
- Admin screens (menu Session Security): Sessions (user, IP, browser, login, last activity, state, Force sign-out), Requests, Log, Settings. Users see their own sessions from Preferences.

**Technical**
- Models: `dwo.session` (state `active|locked|pending_approval|expired`, found by a random key stored in the session so it survives the rotation of the session id), `dwo.user.pin` (salted hash only, no access rights for any group), `dwo.session.request`, `dwo.session.log`, wizard `dwo.pin.wizard`.
- `ir.http._authenticate` gate: every request of a session that is not active is refused (RPC error `dwo_session_locked`, pages redirect to the lock/waiting page, other requests 403); `_serve_fallback` too; the websocket loop (`bus.websocket.check_session`) and the subscription (`ir.websocket._build_bus_channel_list`) follow the same state. Only `/dwo/session/*` and `/web/session/logout` are allowed.
- The lock and waiting pages are server-rendered HTML with inline script: no web client bundle, no session info. The web client leaves for them with `location.replace`, clears IndexedDB and CacheStorage first, and reloads on `pageshow` from bfcache. HTML and JSON responses of signed-in users carry `Cache-Control: no-store`.
- Idle time counts only the explicit activity ping of the browser (mouse, keys, scroll), throttled to one write per 30 s; Odoo's background calls do not count.
- Settings are `ir.config_parameter` `dwo_session.*`; defaults are written once at install (`post_init_hook`): Odoo removes a parameter saved as unchecked or 0, and a missing parameter means off / 0.
- Rescue: set the system parameter `dwo_session.enabled` to 0 (Settings, Technical, System Parameters, or `UPDATE ir_config_parameter SET value='0' WHERE key='dwo_session.enabled'`); every rule is off at once.
- "Save the open form before locking": option, off by default (see the setting help). The lock often comes when nobody can confirm; saving would write data nobody checked. With the option on, the client triggers Odoo's `CLEAR-UNCOMMITTED-CHANGES` (4 s limit) before the lock; a form that cannot be saved is lost. A server-side idle lock (the browser was not running) never saves.

**Versions**: one code base for Odoo 17 to 20. Differences handled in `models/compat.py` (session store and logout moved in 20), `models/util.py` (`icp_get`/`icp_set`: typed parameters in 20), the JSON route type (`json` before 19, `jsonrpc` from 19), the constraint syntax (19+), `res.users.authenticate` (class method before 19), view tags (`tree` in 17) and the access file (`security/ir.access.csv` in 20). Sign out from the lock page is a POST form with a CSRF token (Odoo 20 refuses GET).

**Tests**: HTTP tests (server refusal while locked / waiting, rate limit, redirect safety, CSRF, approval, forgot-PIN ways, timeouts, close browser, cookie header, bus) and two tours in Chrome (expiry dialog back to the same screen, warning toast with Extend). The lock page and the waiting page load no tours: they are covered by the HTTP tests and by a Playwright script run by hand.

**Limits (honest)**
- Data already in the browser before the lock cannot be recalled; navigating away from the page clears its JS heap, and caches of IndexedDB/CacheStorage are cleared, but a user who stops the script (devtools, extension) before the lock keeps what was on screen. The server refuses everything after the lock.
- An already open websocket of a tampered page is closed at its next notification by the state check; messages can still arrive until then.
- Closing the browser: the server cannot see it, it sees that no tab sent a heartbeat for the grace time (180 s by default) or said goodbye (`pagehide`). A browser that restores tabs and cookies (Chrome "Continue where you left off", Safari reopening windows) and is reopened within the grace time keeps the session. A laptop that sleeps longer than the grace time also ends the session. Third party cookie managers or sync of cookies can defeat the check.
- Idle detection is in the browser (mouse, keys, scroll); a script can fake it, but it cannot go beyond the maximum duration.
