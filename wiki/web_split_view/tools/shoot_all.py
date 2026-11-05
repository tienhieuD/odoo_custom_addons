"""Screenshots of web_split_view for one Odoo version (16..20): list with the Split button, split with search and
expand button, new record, back from the full form.   usage: shoot_all.py <version> <out dir>"""
import base64, json, os, shutil, subprocess, sys, tempfile, time
import requests, websocket

V = int(sys.argv[1]); OUT = sys.argv[2]
SRC = {16: 'odoo-16.0.20261021', 17: 'odoo-17.0.20240624', 18: 'odoo-18.0.20260412', 19: 'odoo-19.0.20260412', 20: 'odoo-20.0.20261104'}[V]
ROOT = '/Users/hieu/Documents/Odoo'
CHROME = '/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell'
DB, PORT, CDP = 'splitshot%d' % V, 8500 + V, 9500 + V
W, H = 1366, 800
os.makedirs(OUT, exist_ok=True)

def url(path_new, path_old):
    return path_new if V >= 18 else path_old

conf = open('%s/myproject/odoo_custom_addons%d_conf/odoo.conf' % (ROOT, V)).read()
conf = '\n'.join(l for l in conf.split('\n') if not l.startswith(('dev_mode', 'http_port', 'xmlrpc_port', 'longpolling_port', 'gevent_port')))
cf = '/tmp/splitshot%d.conf' % V
open(cf, 'w').write(conf)
os.chdir('%s/%s' % (ROOT, SRC))
subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
subprocess.run(['docker', 'exec', 'postgres179', 'createdb', '-U', 'odoo', DB], check=True)
demo = ['--with-demo'] if V >= 19 else []
r = subprocess.run(['./venv/bin/python', 'odoo-bin', '-c', cf, '-d', DB, '-i', 'sale_management,web_split_view', '--stop-after-init', '--http-port=%d' % PORT] + demo,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('install exit', r.returncode)
server = subprocess.Popen(['./venv/bin/python', 'odoo-bin', '-c', cf, '-d', DB, '--http-port=%d' % PORT], stdout=open('/tmp/splitshot%d_server.log' % V, 'w'), stderr=subprocess.STDOUT)
for _ in range(120):
    try:
        requests.get('http://127.0.0.1:%d/web/login' % PORT, timeout=2); break
    except Exception:
        time.sleep(1)
s = requests.Session()
s.post('http://127.0.0.1:%d/web/session/authenticate' % PORT, json={'jsonrpc': '2.0', 'method': 'call', 'params': {'db': DB, 'login': 'admin', 'password': 'admin'}})
sid = s.cookies.get('session_id')
profile = tempfile.mkdtemp()
chrome = subprocess.Popen([CHROME, '--remote-debugging-port=%d' % CDP, '--user-data-dir=' + profile, '--no-sandbox', '--disable-gpu',
                           '--hide-scrollbars', '--window-size=%d,%d' % (W, H), 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
ws = websocket.create_connection([t for t in requests.get('http://127.0.0.1:%d/json' % CDP).json() if t['type'] == 'page'][0]['webSocketDebuggerUrl'], timeout=90)
_id = [0]
def call(method, **params):
    _id[0] += 1
    ws.send(json.dumps({'id': _id[0], 'method': method, 'params': params}))
    while True:
        m = json.loads(ws.recv())
        if m.get('id') == _id[0]:
            return m.get('result', m)
def js(expr):
    r = call('Runtime.evaluate', expression=expr, returnByValue=True)
    if 'exceptionDetails' in r:
        raise RuntimeError(str(r['exceptionDetails'])[:300])
    return r['result'].get('value')
def wait_for(cond, timeout=45):
    for _ in range(timeout * 4):
        if js('!!(%s)' % cond):
            return True
        time.sleep(0.25)
    raise TimeoutError(cond)
def shot(name):
    open(os.path.join(OUT, name), 'wb').write(base64.b64decode(call('Page.captureScreenshot', format='png')['data']))
    print('saved', name)
def go(path):
    call('Page.navigate', url='http://127.0.0.1:%d%s' % (PORT, path))
    time.sleep(2)
def enter():
    call('Input.dispatchKeyEvent', type='keyDown', key='Enter', code='Enter', windowsVirtualKeyCode=13)
    call('Input.dispatchKeyEvent', type='keyUp', key='Enter', code='Enter', windowsVirtualKeyCode=13)

call('Emulation.setDeviceMetricsOverride', width=W, height=H, deviceScaleFactor=1, mobile=False)
call('Network.enable')
call('Network.setCookie', name='session_id', value=sid, domain='127.0.0.1', path='/')

LIST = url('/odoo/action-sale.action_orders', '/web#action=sale.action_orders')
SPLIT = url('/odoo/action-sale.action_orders?view_type=split', '/web#action=sale.action_orders&view_type=split')

# 1. the plain list: a Split button appears in the view switcher
go(LIST)
wait_for("document.querySelector('.o_list_view .o_data_row')")
time.sleep(1.5)
shot('screenshot_2.png')

def open_record_with_search():
    go(SPLIT)
    wait_for("document.querySelector('.o_split_view .left-side .o_data_row')")
    time.sleep(1.5)
    js("(() => { const i = document.querySelector('.o_split_view .left-side .o_searchview_input'); i.focus(); })()")
    call('Input.insertText', text='S0001')
    enter()
    time.sleep(2.5)
    js("document.querySelectorAll('.o_split_view .left-side .o_data_row')[1].querySelector('.o_data_cell').click()")
    wait_for("document.querySelector('.o_split_view .right-side .o_form_view .o_field_widget')")
    time.sleep(2.5)

# 2. split with a search and the expand button
open_record_with_search()
shot('screenshot_1.png')

# 3. New: the right pane becomes an empty form
js("document.querySelector('.o_split_button_create').click()")
time.sleep(3)
wait_for("document.querySelector('.o_split_view .right-side .o_form_view .o_field_widget')")
shot('screenshot_3.png')

# 4. expand, then back with the breadcrumb: same place
open_record_with_search()
js("document.querySelector('.o_split_expand').click()")
wait_for("document.querySelector('.o_form_view') && !document.querySelector('.o_split_view')")
time.sleep(2)
js("document.querySelector('.o_control_panel .breadcrumb-item a, .o_control_panel .o_breadcrumb .breadcrumb-item a').click()")
try:
    wait_for("document.querySelector('.o_split_view .left-side .o_data_row.split_active_row')", timeout=20)
except TimeoutError:
    pass
time.sleep(2.5)
print('STATE', js("JSON.stringify({split: !!document.querySelector('.o_split_view'), active: document.querySelectorAll('.o_split_view .split_active_row').length, facets: Array.from(document.querySelectorAll('.o_split_view .o_facet_value, .o_split_view .o_searchview_facet')).map(e => e.textContent.trim().slice(0, 30))})"))
shot('screenshot_4.png')

# 5. settings entry
go(url('/odoo/action-base.res_config_setting_act_window', '/web#action=base.res_config_setting_act_window'))
wait_for("document.querySelector('.o_form_view')")
time.sleep(2)
js("(() => { const t = Array.from(document.querySelectorAll('[data-key]')).find((e) => e.getAttribute('data-key') === 'web_split_view'); if (t) t.click(); })()")
time.sleep(1.5)
shot('settings.png')

ws.close(); chrome.terminate(); server.terminate()
try:
    server.wait(20)
except Exception:
    server.kill()
shutil.rmtree(profile, ignore_errors=True)
subprocess.run(['docker', 'exec', 'postgres179', 'dropdb', '-U', 'odoo', '--if-exists', DB], stderr=subprocess.DEVNULL)
