"""Evidence for dwo_record_concurrency on Odoo 19: two users (admin in the browser, Bob over RPC)."""
import base64, json, os, secrets, subprocess, sys, tempfile, time
import requests, websocket

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listing')
ROOT = os.path.expanduser('~/Documents/Project')
SRC = 'odoo-19.0.20260412'
CHROME = '/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell'
DB, PORT, CDP = 'concshot19', 8619, 9619
W, H = 1366, 800
LOG = []
# throw-away user of a throw-away database: the password is generated for each run, never stored
BOB_PASSWORD = secrets.token_urlsafe(16)

conf = open(f'{ROOT}/odoo_appstore/_conf/odoo19.conf').read()
conf = '\n'.join(l for l in conf.split('\n') if not l.startswith(('dev_mode', 'http_port', 'xmlrpc_port', 'longpolling_port', 'gevent_port')))
open('/tmp/concshot.conf', 'w').write(conf)
os.chdir(f'{ROOT}/{SRC}')
subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
subprocess.run(['docker', 'exec', 'postgres179', 'createdb', '-U', 'odoo', DB], check=True)
r = subprocess.run(['./venv/bin/python', 'odoo-bin', '-c', '/tmp/concshot.conf', '-d', DB, '-i', 'dwo_record_concurrency,contacts', '--stop-after-init', f'--http-port={PORT}'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('install exit', r.returncode)
server = subprocess.Popen(['./venv/bin/python', 'odoo-bin', '-c', '/tmp/concshot.conf', '-d', DB, f'--http-port={PORT}'], stdout=open('/tmp/concshot_server.log', 'w'), stderr=subprocess.STDOUT)
for _ in range(120):
    try:
        requests.get(f'http://127.0.0.1:{PORT}/web/login', timeout=2); break
    except Exception:
        time.sleep(1)

BASE = f'http://127.0.0.1:{PORT}'
def session(login, pw):
    s = requests.Session()
    s.post(f'{BASE}/web/session/authenticate', json={'jsonrpc': '2.0', 'method': 'call', 'params': {'db': DB, 'login': login, 'password': pw}})
    return s
def rpc(s, model, method, args, kwargs=None):
    r = s.post(f'{BASE}/web/dataset/call_kw/{model}/{method}', json={'jsonrpc': '2.0', 'method': 'call', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs or {}}}).json()
    if 'error' in r:
        raise RuntimeError(str(r['error'])[:400])
    return r['result']

admin = session('admin', 'admin')
gid = rpc(admin, 'ir.model.data', 'search_read', [[['module', '=', 'base'], ['name', '=', 'group_partner_manager']], ['res_id']])[0]['res_id']
gfield = 'group_ids' if rpc(admin, 'res.users', 'fields_get', [['group_ids']]) else 'groups_id'
rpc(admin, 'res.users', 'create', [[{'name': 'Bob Martin', 'login': 'bob', 'password': BOB_PASSWORD, gfield: [[4, gid], [4, rpc(admin, 'ir.model.data', 'search_read', [[['module', '=', 'base'], ['name', '=', 'group_user']], ['res_id']])[0]['res_id']]]}]])
bob = session('bob', BOB_PASSWORD)
model_id = rpc(admin, 'ir.model', 'search', [[['model', '=', 'res.partner']]])[0]
fids = rpc(admin, 'ir.model.fields', 'search', [[['model', '=', 'res.partner'], ['name', 'in', ['name', 'phone']]]])
cfg = rpc(admin, 'dwo.model.concurrency', 'create', [[{'model_id': model_id, 'field_ids': [[6, 0, fids]]}]])[0]
partner = rpc(admin, 'res.partner', 'create', [[{'name': 'Azure Interior', 'phone': '+1 555-0100', 'website': 'https://azure.example.com'}]])[0]
def srv(field):
    return rpc(admin, 'res.partner', 'read', [[partner], [field]])[0][field]

profile = tempfile.mkdtemp()
chrome = subprocess.Popen([CHROME, f'--remote-debugging-port={CDP}', '--user-data-dir=' + profile, '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--window-size={W},{H}', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
ws = websocket.create_connection([t for t in requests.get(f'http://127.0.0.1:{CDP}/json').json() if t['type'] == 'page'][0]['webSocketDebuggerUrl'], timeout=90)
_id = [0]; ERRS = []; WS = []
def call(method, **params):
    _id[0] += 1
    ws.send(json.dumps({'id': _id[0], 'method': method, 'params': params}))
    while True:
        m = json.loads(ws.recv())
        if m.get('method') == 'Runtime.exceptionThrown':
            d = m['params']['exceptionDetails']; ERRS.append((d.get('exception') or {}).get('description') or d.get('text'))
        if m.get('method') == 'Runtime.consoleAPICalled' and any('DWO' in str(a.get('value', '')) for a in m['params']['args']):
            WS.append(' '.join(str(a.get('value')) for a in m['params']['args'])[:700])
        if str(m.get('method', '')).startswith('Network.webSocket'):
            WS.append(m['method'] + ' ' + json.dumps(m['params'])[:160])
        if m.get('id') == _id[0]:
            return m.get('result', m)
def js(expr):
    r = call('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
    if 'exceptionDetails' in r:
        raise RuntimeError(str(r['exceptionDetails'].get('exception', {}).get('description', r['exceptionDetails']))[:500])
    return r['result'].get('value')
def wait_for(cond, timeout=30):
    for _ in range(timeout * 4):
        if js(f'!!({cond})'):
            return True
        time.sleep(0.25)
    print('DOM:', js("[...document.querySelectorAll('[name=name]')].map(e=>e.outerHTML.slice(0,300)).join('|')"))
    open(os.path.join(OUT, 'debug_timeout.png'), 'wb').write(base64.b64decode(call('Page.captureScreenshot', format='png')['data']))
    raise TimeoutError(cond)
def shot(name, note):
    open(os.path.join(OUT, name), 'wb').write(base64.b64decode(call('Page.captureScreenshot', format='png')['data']))
    LOG.append(f'{name}: {note}'); print('saved', name, '-', note)
def go(path):
    call('Page.navigate', url=BASE + path); time.sleep(2.5)
def type_into(sel, text):
    js(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); e.focus(); e.select(); }})()")
    call('Input.insertText', text=text); time.sleep(0.4)
def click(sel):
    js(f"document.querySelector({json.dumps(sel)}).click()"); time.sleep(0.6)


def HIDE(close_toast=False):
    css = ".o_debug_manager, .oe_topbar_name {display: none !important}"
    if close_toast:
        css += " .o_notification_manager {display: none !important}"
    js("(() => { let st = document.getElementById('dwo_hide'); if (!st) { st = document.createElement('style'); st.id = 'dwo_hide'; document.head.appendChild(st); } st.textContent = %s; })()" % json.dumps(css))
    time.sleep(0.4)

call('Page.enable'); call('Runtime.enable')
call('Network.enable')
call('Network.setCookie', name='session_id', value=admin.cookies.get('session_id'), url=BASE)
NAME = ".o_form_view .o_field_widget[name=name] input, .o_form_view .o_field_widget[name=name] textarea"
PHONE = ".o_form_view .o_field_widget[name=phone] input"

# 1 configuration screen (admin)
go(f'/odoo/action-dwo_record_concurrency.action_dwo_model_concurrency_views/{cfg}')
wait_for("document.querySelector('.o_form_view')")
time.sleep(1)
shot('screenshot_3.png', 'Settings > Concurrency: model res.partner, watched fields Name and Phone')

# ---------------- scenario A: same field changed by Bob -> dialog
url = f'/odoo/action-base.action_partner_form/{partner}'
go(url + '?debug=1'); wait_for(f"document.querySelector('{NAME}')"); time.sleep(1.5)
print('bus active:', js("(() => { const b = odoo.__WOWL_DEBUG__.root.env.services.bus_service; b.addEventListener('notification', e => console.debug('DWO raw ' + JSON.stringify(e.detail))); return b.isActive; })()"))
HIDE(); shot('x_unused_02.png', 'Admin opens the partner form (snapshot of the watched fields is taken)')
type_into(NAME, 'Azure Interior (my edit)')
shot('x_unused_03.png', 'Admin edits the name, not saved yet (form is dirty)')
rpc(bob, 'res.partner', 'write', [[partner], {'name': 'Azure Interior SARL'}])
time.sleep(1)
row = subprocess.run(['docker', 'exec', 'postgres179', 'psql', '-U', 'odoo', '-d', DB, '-Atc',
                      "select message from bus_bus where message like '%\"Bob Martin\"%' order by id desc limit 1"], capture_output=True, text=True).stdout.strip()
LOG.append('payload written by the server for Bob save: ' + row)
js("odoo.__WOWL_DEBUG__.root.env.services.bus_service.trigger('notification', [%s])" % row)
time.sleep(1)
print('toasts:', js("document.querySelectorAll('.o_notification').length"))
HIDE(); shot('screenshot_2.png', 'Bob saves the same field: toast shown by the client. NOTE: the websocket delivery is simulated here (the exact payload the server stored in bus_bus is replayed into bus_service) because the headless sandbox cannot deliver any bus message, not even a core broadcast')
click('.o_form_button_save'); wait_for("document.querySelector('.modal')"); time.sleep(0.6)
HIDE(True); shot('screenshot_1.png', 'Admin clicks Save: dialog with Your Updates / Latest Data, last updated by Bob')
click(".modal button.btn-link")  # Cancel
time.sleep(0.8)
shot('x_unused_06.png', 'Cancel: nothing saved, admin still has the edits; server value untouched = ' + srv('name'))
click('.o_form_button_save'); wait_for("document.querySelector('.modal')")
LOG.append('server name before Force Save: ' + srv('name'))
click(".modal button.btn-primary")  # Force Save
time.sleep(1.5)
shot('x_unused_07.png', 'Force Save: admin value written. server name = ' + srv('name'))
assert srv('name') == 'Azure Interior (my edit)', srv('name')


rows = ''
LOG.append('listing screenshots done')
open(os.path.join(OUT, 'evidence.txt'), 'w').write('\n'.join(LOG))
chrome.terminate(); server.terminate()
subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
