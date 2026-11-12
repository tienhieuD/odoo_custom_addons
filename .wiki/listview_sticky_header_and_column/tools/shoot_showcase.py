"""Take the two description screenshots (outer list pinned + list inside a form pinned) for one Odoo version.

usage: svgenv/bin/python shoot.py <version> <out dir>
"""
import base64, json, os, shutil, subprocess, sys, tempfile, time
import requests, websocket

V = int(sys.argv[1])
OUTDIR = sys.argv[2]
SRC = {12: 'odoo-12.0.20211011', 13: 'odoo-13.0.20230607', 14: 'odoo-14.0.20231205', 15: 'odoo-15.0.20250115',
       16: 'odoo-16.0.20261021', 17: 'odoo-17.0.20240624', 18: 'odoo-18.0.20260412', 19: 'odoo-19.0.20260412',
       20: 'odoo-20.0.20261104'}[V]
ROOT = os.path.expanduser('~/Documents/Project')
CHROME = '/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell'
DB = 'shot%d' % V
PORT = 8400 + V
CDP = 9300 + V
W, H = 1100, 860
URL = ('http://127.0.0.1:%d/odoo/action-listview_sticky_test_lab.action_lshc_test_showcase' if V >= 18
       else 'http://127.0.0.1:%d/web#action=listview_sticky_test_lab.action_lshc_test_showcase') % PORT

os.makedirs(OUTDIR, exist_ok=True)
conf = open('%s/odoo_appstore/_conf/odoo%d.conf' % (ROOT, V)).read()
conf = '\n'.join(l for l in conf.split('\n') if not l.startswith(('dev_mode', 'http_port', 'xmlrpc_port', 'longpolling_port', 'gevent_port')))
tmpconf = '/tmp/shot%d.conf' % V
open(tmpconf, 'w').write(conf)
os.chdir('%s/%s' % (ROOT, SRC))
py = './venv/bin/python'
demo = ['--with-demo'] if V >= 19 else []

def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)

subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
subprocess.run(['docker', 'exec', 'postgres179', 'createdb', '-U', 'odoo', DB], check=True)
r = run([py, 'odoo-bin', '-c', tmpconf, '-d', DB, '-i', 'listview_sticky_test_lab', '--stop-after-init', '--http-port=%d' % PORT] + demo)
print('install exit', r.returncode)
server = subprocess.Popen([py, 'odoo-bin', '-c', tmpconf, '-d', DB, '--http-port=%d' % PORT, '--workers=0'],
                          stdout=open('/tmp/shot%d_server.log' % V, 'w'), stderr=subprocess.STDOUT)
for _ in range(60):
    try:
        requests.get('http://127.0.0.1:%d/web/login' % PORT, timeout=2)
        break
    except Exception:
        time.sleep(1)

# login through JSON-RPC
s = requests.Session()
resp = s.post('http://127.0.0.1:%d/web/session/authenticate' % PORT, json={'jsonrpc': '2.0', 'method': 'call', 'params': {'db': DB, 'login': 'admin', 'password': 'admin'}})
sid = s.cookies.get('session_id')
print('login', resp.json().get('result', {}).get('uid'), bool(sid))

profile = tempfile.mkdtemp()
chrome = subprocess.Popen([CHROME, '--remote-debugging-port=%d' % CDP, '--user-data-dir=' + profile, '--no-sandbox', '--disable-gpu',
                           '--hide-scrollbars', '--window-size=%d,%d' % (W, H), 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
ws_url = [t for t in requests.get('http://127.0.0.1:%d/json' % CDP).json() if t['type'] == 'page'][0]['webSocketDebuggerUrl']
ws = websocket.create_connection(ws_url, timeout=60)
_id = [0]

def call(method, **params):
    _id[0] += 1
    ws.send(json.dumps({'id': _id[0], 'method': method, 'params': params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == _id[0]:
            return msg.get('result', msg)

def js(expr, wait=True):
    r = call('Runtime.evaluate', expression=expr, awaitPromise=wait, returnByValue=True)
    if 'exceptionDetails' in r:
        raise RuntimeError(r['exceptionDetails'].get('exception', {}).get('description', str(r['exceptionDetails'])))
    return r['result'].get('value')

def wait_for(cond, timeout=40):
    for _ in range(timeout * 4):
        if js('!!(%s)' % cond, wait=False):
            return True
        time.sleep(0.25)
    raise TimeoutError(cond)

def shot(name):
    data = call('Page.captureScreenshot', format='png')['data']
    path = os.path.join(OUTDIR, name)
    open(path, 'wb').write(base64.b64decode(data))
    print('saved', path)

HELPERS = r'''
window.__lab = {
  sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  th: (root, name) => Array.from(root.querySelectorAll('thead th')).find((t) => (t.getAttribute('data-name') || (window.$ && $(t).data('name'))) === name),
  scroller: (el) => { let p = el.parentElement; while (p) { const o = getComputedStyle(p); if (/(auto|scroll)/.test(o.overflowX + o.overflowY) && (p.scrollWidth > p.clientWidth || p.scrollHeight > p.clientHeight)) { return p; } p = p.parentElement; } return document.scrollingElement; },
  tableOf: (root) => root.tagName === 'TABLE' ? root : root.querySelector('table'),
};
'''

call('Emulation.setDeviceMetricsOverride', width=W, height=H, deviceScaleFactor=1, mobile=False)
call('Network.enable')
call('Network.setCookie', name='session_id', value=sid, domain='127.0.0.1', path='/')
call('Page.navigate', url=URL)
wait_for("document.querySelector('.o_list_view .o_data_row')")
time.sleep(1.5)
js(HELPERS, wait=False)

# ---------------------------------------------------------------- screenshot 1: the list, one column pinned, scrolled
print('scrollLeft list', js('''(async () => {
  const L = window.__lab;
  const root = document.querySelector('.o_list_view');
  const th = L.th(root, 'partner_id');
  th.querySelector('.js_pin_this_column').click();
  await L.sleep(1200);
  const sc = L.scroller(L.tableOf(root));
  sc.scrollLeft = 300;
  sc.scrollTop = 120;
  await L.sleep(600);
  return sc.scrollLeft;
})()'''))
rect = js('''(() => { const L = window.__lab; const th = L.th(document.querySelector('.o_list_view'), 'partner_id'); const r = th.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()''', wait=False)
call('Input.dispatchMouseEvent', type='mouseMoved', x=rect[0], y=rect[1])
time.sleep(0.6)
shot('screenshot_1.png')

# ---------------------------------------------------------------- screenshot 2: the list inside a form
js('''(() => { document.querySelector('.o_list_view tbody tr.o_data_row td:nth-child(3)').click(); })()''', wait=False)
wait_for("document.querySelector('.o_form_view .o_field_widget[name=line_medium_ids] tbody tr')")
time.sleep(1.5)
js(HELPERS, wait=False)
print('scrollLeft form', js('''(async () => {
  const L = window.__lab;
  const root = document.querySelector('.o_form_view .o_field_widget[name=line_medium_ids]');
  const th = L.th(root, 'product');
  th.querySelector('.js_pin_this_column').click();
  await L.sleep(1200);
  const sc = L.scroller(L.tableOf(root));
  sc.scrollLeft = 300;
  await L.sleep(500);
  return sc.scrollLeft;
})()'''))
rect = js('''(() => { const L = window.__lab; const th = L.th(document.querySelector('.o_form_view .o_field_widget[name=line_medium_ids]'), 'product'); const r = th.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()''', wait=False)
call('Input.dispatchMouseEvent', type='mouseMoved', x=rect[0], y=rect[1])
time.sleep(0.6)
shot('screenshot_2.png')

ws.close()
chrome.terminate()
server.terminate()
try:
    server.wait(20)
except Exception:
    server.kill()
shutil.rmtree(profile, ignore_errors=True)
subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
