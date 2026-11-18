# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The lock page and the waiting page: plain HTML built on the server, with a few lines of inline script.
They load no Odoo web client and carry no application data: only the name of the user and what they must do."""
from html import escape

from odoo.addons.dwo_session_security.models.util import cfg_bool, tr

CSS = """
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
background:#1f2933;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1f2933}
.card{background:#fff;border-radius:12px;box-shadow:0 20px 50px rgba(0,0,0,.35);padding:32px 36px;width:min(92vw,400px);text-align:center}
.lock{width:56px;height:56px;border-radius:50%;background:#875a7b;color:#fff;display:flex;align-items:center;justify-content:center;
font-size:26px;margin:0 auto 14px}h1{font-size:20px;margin:0 0 4px}p{margin:6px 0;color:#52606d;font-size:14px}
input[type=password],input[type=text]{width:100%;font-size:22px;letter-spacing:.35em;text-align:center;padding:10px;border:1px solid #cbd2d9;
border-radius:8px;margin:12px 0 4px}input.plain{letter-spacing:normal;font-size:16px}
button,.btn{display:inline-block;width:100%;background:#875a7b;color:#fff;border:0;border-radius:8px;padding:11px;font-size:15px;
cursor:pointer;margin-top:10px;text-decoration:none}.btn.light,button.light{background:#e4e7eb;color:#1f2933}
.err{background:#fde8e8;color:#b42318;border-radius:8px;padding:8px 10px;font-size:13px;margin-top:10px}
.ok{background:#e6f6ec;color:#0e7c66;border-radius:8px;padding:8px 10px;font-size:13px;margin-top:10px}
details{margin-top:16px;text-align:left}summary{cursor:pointer;color:#875a7b;font-size:14px;text-align:center}
details form{margin-top:8px}.small{font-size:12px;color:#7b8794;margin-top:14px}
@keyframes spin{to{transform:rotate(360deg)}}.spin{width:34px;height:34px;border:4px solid #e4e7eb;border-top-color:#875a7b;
border-radius:50%;animation:spin 1s linear infinite;margin:16px auto}
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
setInterval(beat,3000);beat();
window.addEventListener('pageshow',function(e){if(e.persisted){location.reload()}});
window.addEventListener('pagehide',function(e){if(!e.persisted&&navigator.sendBeacon){try{navigator.sendBeacon('/dwo/session/bye',new Blob([JSON.stringify({jsonrpc:'2.0',method:'call',params:{tab:tab}})],{type:'application/json'}))}catch(x){}}});
})();
"""


def layout(env, title, body, want, reset="", canset=False):
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>%s</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex\">"
        "<style>%s</style></head><body data-want=\"%s\" data-reset=\"%s\" data-canset=\"%s\">%s<script>%s</script></body></html>"
        % (escape(title), CSS, want, escape(reset or ""), "1" if canset else "", body, SCRIPT)
    )


def _csrf(token):
    return '<input type="hidden" name="csrf_token" value="%s"/>' % escape(token)


def message(kind, text):
    return '<div class="%s">%s</div>' % (kind, escape(text)) if text else ""


def lock_page(env, row, csrf, error=None, notice=None, otp=False):
    t = lambda m, *a: tr(env, m, *a)   # noqa: E731
    user = row.user_id

    pin = env["dwo.user.pin"]._of(user.id)
    req = row.approval_id if row.approval_id and row.approval_id.kind == "pin_reset" else False
    reset_state = req.state if req else ""
    parts = ['<div class="card"><div class="lock">&#128274;</div>']
    if row.can_set_pin:
        parts.append("<h1>%s</h1><p>%s</p>" % (escape(t("Choose a new PIN")), escape(
            t("Use 4 or 6 digits. Avoid easy ones such as 1234 or 0000."))))
        parts.append(message("err", error) + message("ok", notice))
        parts.append('<form method="post" action="/dwo/session/setpin">%s'
                     '<input type="password" name="pin" inputmode="numeric" pattern="[0-9]*" maxlength="6" autocomplete="new-password" autofocus required placeholder="PIN"/>'
                     '<input type="password" name="pin2" inputmode="numeric" pattern="[0-9]*" maxlength="6" autocomplete="new-password" required placeholder="%s"/>'
                     '<button type="submit">%s</button></form>' % (_csrf(csrf), escape(t("Repeat the PIN")), escape(t("Save the PIN"))))
    else:
        parts.append("<h1>%s</h1><p>%s</p>" % (escape(t("Screen locked")), escape(user.name or "")))
        parts.append(message("err", error) + message("ok", notice))
        wait = pin.seconds_locked() if pin else 0
        if pin and pin.pin_hash:
            parts.append('<form method="post" action="/dwo/session/unlock">%s'
                         '<input type="password" name="pin" inputmode="numeric" pattern="[0-9]*" maxlength="6" autocomplete="off" autofocus required placeholder="PIN"/>'
                         '<button type="submit">%s</button></form>' % (_csrf(csrf), escape(t("Unlock"))))
        else:
            parts.append("<p>%s</p>" % escape(t("There is no PIN for this account. Use one of the options below.")))
        if wait:
            parts.append(message("err", t("Too many wrong PINs. Wait %s seconds.", wait)))
        options = []
        if cfg_bool(env, "forgot_relogin"):
            if user._dwo_has_password():
                options.append('<form method="post" action="/dwo/session/unlock_password">%s<p>%s</p>'
                               '<input type="password" class="plain" name="password" autocomplete="current-password" placeholder="%s"/>'
                               '<button type="submit" class="light">%s</button></form>'
                               % (_csrf(csrf), escape(t("Enter the password of your account:")), escape(t("Password")),
                                  escape(t("Unlock with my password"))))
            options.append('<a class="btn light" href="/dwo/session/relogin">%s</a>' % escape(t("Sign in again")))
        if cfg_bool(env, "forgot_admin"):
            if reset_state == "pending":
                options.append('<p><b>%s</b></p>' % escape(t("Waiting for an administrator to reset your PIN...")))
            else:
                options.append('<form method="post" action="/dwo/session/request_reset">%s<button type="submit" class="light">%s</button></form>'
                               % (_csrf(csrf), escape(t("Ask an administrator to reset my PIN"))))
                if reset_state == "rejected":
                    options.append(message("err", t("The administrator refused the reset.")))
        if cfg_bool(env, "forgot_otp") and user.email:
            if otp:
                options.append('<form method="post" action="/dwo/session/verify_otp">%s<p>%s</p>'
                               '<input type="text" name="code" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="000000"/>'
                               '<button type="submit" class="light">%s</button></form>'
                               % (_csrf(csrf), escape(t("Enter the 6-digit code we sent to your email (valid 10 minutes).")),
                                  escape(t("Check the code"))))
            else:
                options.append('<form method="post" action="/dwo/session/send_otp">%s<button type="submit" class="light">%s</button></form>'
                               % (_csrf(csrf), escape(t("Email me a code"))))
        if options:
            parts.append("<details%s><summary>%s</summary>%s</details>" % (
                " open" if (otp or reset_state in ("pending", "rejected")) else "", escape(t("Forgot the PIN?")), "".join(options)))
    parts.append('<p class="small"><a href="/web/session/logout?redirect=/web/login">%s</a></p>' % escape(t("Sign out")))
    parts.append("</div>")
    return layout(env, t("Screen locked"), "".join(parts), "locked", reset_state, row.can_set_pin)


def waiting_page(env, row):
    t = lambda m, *a: tr(env, m, *a)   # noqa: E731
    body = ('<div class="card"><div class="lock">&#9203;</div><h1>%s</h1><p>%s</p><div class="spin"></div>'
            '<p class="small">%s</p><p class="small"><a href="/web/session/logout?redirect=/web/login">%s</a></p></div>'
            % (escape(t("Waiting for approval")),
               escape(t("An administrator has to approve this sign-in before you can enter. This page opens Odoo as soon as it is approved.")),
               escape(row.user_id.name or ""), escape(t("Cancel and sign out"))))
    return layout(env, t("Waiting for approval"), body, "waiting")
