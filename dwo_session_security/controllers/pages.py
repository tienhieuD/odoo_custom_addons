# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The lock page and the waiting page: plain HTML built on the server, with a few lines of inline script.
They load no Odoo web client and carry no application data: only the name of the user and what they must do."""
from html import escape

from odoo.addons.dwo_session_security.models.util import cfg_bool, tr

# Only the CSS of the bundle that Odoo's own login page uses is loaded (template page_css): no script, no data.
# The few rules below only centre the lock icon and keep the details list readable.
CSS = """
.dwo-icon{width:56px;height:56px;border-radius:50%;background:var(--bs-primary,#714B67);color:#fff;display:flex;align-items:center;
justify-content:center;font-size:26px;margin:0 auto 12px}
.dwo-pin{letter-spacing:.35em;font-size:1.4rem}.dwo-pin::placeholder{letter-spacing:normal;font-size:1rem}.dwo-options form{margin-top:.5rem}
"""

SCRIPT = """
(function(){
var b=document.body, tab=null;
try{tab=sessionStorage.getItem('dwo_tab')}catch(e){}
if(!tab){tab=Math.random().toString(36).slice(2)+Date.now().toString(36);try{sessionStorage.setItem('dwo_tab',tab)}catch(e){}}
var want=b.getAttribute('data-want'), reset=b.getAttribute('data-reset')||'', canset=b.getAttribute('data-canset')||'';
var chan=null;try{chan=new BroadcastChannel('dwo_session');chan.onmessage=function(m){if(m.data&&m.data.type==='unlocked'){location.reload()}}}catch(e){}
function beat(){
 fetch('/dwo/session/heartbeat',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({jsonrpc:'2.0',method:'call',params:{tab:tab},id:1})}).then(function(r){return r.json()}).then(function(j){
  var s=j.result||{state:'expired'};
  if(s.state==='active'){if(chan){try{chan.postMessage({type:'unlocked'})}catch(e){}};location.replace('/dwo/session/resume')}
  else if(s.state==='expired'){location.replace('/dwo/session/relogin')}
  else if(want==='locked' && ((s.reset||'')!==reset || String(!!s.can_set_pin)!==(canset?'true':'false'))){location.reload()}
 }).catch(function(){});
}
(function(){var f=document.querySelectorAll('input[data-auto]');f.forEach(function(el){var done=false;
 el.addEventListener('input',function(){var v=el.value.replace(/\D/g,'');if(v!==el.value){el.value=v}
  var n=parseInt(el.getAttribute('data-auto'),10);
  if(!done&&n>0&&v.length===n){var other=el.getAttribute('data-match');if(other){var o=document.querySelector('input[name='+other+']');if(!o||o.value!==v){return}}
   done=true;el.form.requestSubmit?el.form.requestSubmit():el.form.submit()}})})})();
setInterval(beat,3000);beat();
window.addEventListener('pageshow',function(e){if(e.persisted){location.reload()}});
window.addEventListener('pagehide',function(e){if(!e.persisted&&navigator.sendBeacon){try{navigator.sendBeacon('/dwo/session/bye',new Blob([JSON.stringify({jsonrpc:'2.0',method:'call',params:{tab:tab}})],{type:'application/json'}))}catch(x){}}});
})();
"""


def layout(env, title, body, want, reset="", canset=False):
    css = env["ir.qweb"]._render("dwo_session_security.page_css")
    card = (
        '<div class="container py-5"><div class="card border-0 mx-auto bg-100" style="max-width: 300px;"><div class="card-body">'
        '<div class="text-center pb-3 border-bottom mb-4"><img src="/web/binary/company_logo" alt="Logo" '
        'style="max-height:120px; max-width: 100%%; width:auto"/></div>%s</div></div></div>' % body
    )
    return (
        "<!DOCTYPE html><html lang=\"en\" style=\"height: 100%%;\"><head><meta charset=\"utf-8\"><title>%s</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex\">"
        "%s<style>%s</style></head><body class=\"bg-100\" data-want=\"%s\" data-reset=\"%s\" data-canset=\"%s\">%s<script>%s</script></body></html>"
        % (escape(title), css, CSS, want, escape(reset or ""), "1" if canset else "", card, SCRIPT)
    )


def _csrf(token):
    return '<input type="hidden" name="csrf_token" value="%s"/>' % escape(token)


def signout(csrf, label):
    """Odoo 20 only signs out with a POST: a small form works everywhere."""
    return ('<form class="mb-0" method="post" action="/web/session/logout?redirect=/web/login">%s'
            '<button type="submit" class="btn btn-link btn-sm">%s</button></form>' % (_csrf(csrf), escape(label)))


def message(kind, text):
    cls = {"err": "alert alert-danger", "ok": "alert alert-success"}.get(kind, "alert alert-info")
    return '<p class="%s" role="alert">%s</p>' % (cls, escape(text)) if text else ""


def _pin_input(name, placeholder, auto=0, match="", autofocus=False, new=False):
    return ('<input type="password" name="%s" class="form-control form-control-lg text-center dwo-pin mb-2" inputmode="numeric" '
            'pattern="[0-9]*" maxlength="6" autocomplete="%s" %s required="required" aria-label="%s" placeholder="%s"%s%s/>'
            % (name, "new-password" if new else "off", "autofocus" if autofocus else "", escape(placeholder), escape(placeholder),
               ' data-auto="%d"' % auto if auto else "", ' data-match="%s"' % match if match else ""))


def lock_page(env, row, csrf, error=None, notice=None, otp=False):
    t = lambda m, *a: tr(env, m, *a)   # noqa: E731
    user = row.user_id
    pin = env["dwo.user.pin"]._of(user.id)
    req = row.approval_id if row.approval_id and row.approval_id.kind == "pin_reset" else False
    reset_state = req.state if req else ""
    length = pin.length if pin and pin.length in (4, 6) else 0
    parts = ['<div class="dwo-icon" aria-hidden="true">&#128274;</div>']
    if row.can_set_pin:
        parts.append('<h4 class="text-center">%s</h4><p class="text-center text-muted small">%s</p>' % (
            escape(t("Choose a new PIN")), escape(t("Use 4 or 6 digits. Avoid easy ones such as 1234 or 0000."))))
        parts.append(message("err", error) + message("ok", notice))
        parts.append('<form method="post" action="/dwo/session/setpin">%s%s%s'
                     '<div class="d-grid"><button type="submit" class="btn btn-primary">%s</button></div></form>'
                     % (_csrf(csrf), _pin_input("pin", "PIN", autofocus=True, new=True),
                        _pin_input("pin2", t("Repeat the PIN"), auto=4, match="pin", new=True), escape(t("Save the PIN"))))
    else:
        parts.append('<h4 class="text-center mb-0">%s</h4><p class="text-center text-muted">%s</p>' % (
            escape(t("Screen locked")), escape(user.name or "")))
        parts.append(message("err", error) + message("ok", notice))
        wait = pin.seconds_locked() if pin else 0
        if pin and pin.pin_hash:
            parts.append('<form method="post" action="/dwo/session/unlock">%s%s'
                         '<div class="d-grid"><button type="submit" class="btn btn-primary">%s</button></div></form>'
                         % (_csrf(csrf), _pin_input("pin", "PIN", auto=length, autofocus=True), escape(t("Unlock"))))
        else:
            parts.append('<p class="text-muted">%s</p>' % escape(t("There is no PIN for this account. Use one of the options below.")))
        if wait:
            parts.append(message("err", t("Too many wrong PINs. Wait %s seconds.", wait)))
        options = []
        if cfg_bool(env, "forgot_relogin"):
            if user._dwo_has_password():
                options.append('<form method="post" action="/dwo/session/unlock_password">%s<label class="form-label small" for="dwo_pw">%s</label>'
                               '<input type="password" id="dwo_pw" class="form-control mb-2" name="password" autocomplete="current-password"/>'
                               '<div class="d-grid"><button type="submit" class="btn btn-secondary">%s</button></div></form>'
                               % (_csrf(csrf), escape(t("Enter the password of your account:")), escape(t("Unlock with my password"))))
            options.append('<div class="d-grid mt-2"><a class="btn btn-secondary" href="/dwo/session/relogin">%s</a></div>' % escape(t("Sign in again")))
        if cfg_bool(env, "forgot_admin"):
            if reset_state == "pending":
                options.append('<p class="mt-2"><b>%s</b></p>' % escape(t("Waiting for an administrator to reset your PIN...")))
            else:
                options.append('<form method="post" action="/dwo/session/request_reset">%s<div class="d-grid mt-2"><button type="submit" class="btn btn-secondary">%s</button></div></form>'
                               % (_csrf(csrf), escape(t("Ask an administrator to reset my PIN"))))
                if reset_state == "rejected":
                    options.append(message("err", t("The administrator refused the reset.")))
        if cfg_bool(env, "forgot_otp") and user.email:
            if otp:
                options.append('<form method="post" action="/dwo/session/verify_otp">%s<label class="form-label small mt-2" for="dwo_otp">%s</label>'
                               '<input type="text" id="dwo_otp" name="code" class="form-control text-center dwo-pin mb-2" inputmode="numeric" maxlength="6" '
                               'autocomplete="off" data-auto="6" placeholder="000000"/>'
                               '<div class="d-grid"><button type="submit" class="btn btn-secondary">%s</button></div></form>'
                               % (_csrf(csrf), escape(t("Enter the 6-digit code we sent to your email (valid 10 minutes).")), escape(t("Check the code"))))
            else:
                options.append('<form method="post" action="/dwo/session/send_otp">%s<div class="d-grid mt-2"><button type="submit" class="btn btn-secondary">%s</button></div></form>'
                               % (_csrf(csrf), escape(t("Email me a code"))))
        if options:
            parts.append('<details class="dwo-options mt-3"%s><summary class="text-center text-primary" style="cursor:pointer">%s</summary>%s</details>' % (
                " open" if (otp or reset_state in ("pending", "rejected")) else "", escape(t("Forgot the PIN?")), "".join(options)))
    parts.append('<div class="text-center small mt-4 pt-3 border-top">%s</div>' % signout(csrf, t("Sign out")))
    return layout(env, t("Screen locked"), "".join(parts), "locked", reset_state, row.can_set_pin)


def waiting_page(env, row, csrf):
    t = lambda m, *a: tr(env, m, *a)   # noqa: E731
    body = ('<div class="dwo-icon" aria-hidden="true">&#9203;</div><h4 class="text-center">%s</h4>'
            '<p class="text-center text-muted" role="status">%s</p><div class="text-center my-3"><div class="spinner-border text-primary" role="presentation"></div></div>'
            '<p class="text-center small text-muted">%s</p><div class="text-center small mt-4 pt-3 border-top">%s</div>'
            % (escape(t("Waiting for approval")),
               escape(t("An administrator has to approve this sign-in before you can enter. This page opens Odoo as soon as it is approved.")),
               escape(row.user_id.name or ""), signout(csrf, t("Cancel and sign out"))))
    return layout(env, t("Waiting for approval"), body, "waiting")
