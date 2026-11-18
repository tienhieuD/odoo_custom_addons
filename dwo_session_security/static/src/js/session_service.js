/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const CHANNEL = "dwo_session";
const INPUT_EVENTS = ["mousemove", "mousedown", "keydown", "wheel", "touchstart", "scroll"];

function tabId() {
    let tab = null;
    try {
        tab = sessionStorage.getItem("dwo_tab");
    } catch {
        /* storage blocked */
    }
    if (!tab) {
        tab = Math.random().toString(36).slice(2) + Date.now().toString(36);
        try {
            sessionStorage.setItem("dwo_tab", tab);
        } catch {
            /* storage blocked */
        }
    }
    return tab;
}

async function post(url, params) {
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: params || {}, id: Date.now() }),
    });
    const data = await response.json();
    return data.result;
}

export const dwoSessionService = {
    dependencies: ["dialog", "notification"],
    start(env, { dialog, notification }) {
        const tab = tabId();
        let channel = null;
        try {
            channel = new BroadcastChannel(CHANNEL);
        } catch {
            /* no BroadcastChannel */
        }
        let cfg = null;
        let state = "active";
        let lastInput = Date.now();
        let lastShared = 0;
        let locking = false;
        let toastClose = null;
        let toastMinute = null;
        let warned = false;

        // -- forget what the page holds, then leave it for a server-rendered page --------------------------
        async function purge() {
            document.documentElement.style.visibility = "hidden";
            const jobs = [];
            try {
                if (indexedDB.databases) {
                    jobs.push(
                        indexedDB.databases().then((dbs) =>
                            dbs.forEach((db) => db.name && indexedDB.deleteDatabase(db.name))
                        )
                    );
                }
                if (window.caches) {
                    jobs.push(caches.keys().then((keys) => keys.forEach((key) => caches.delete(key))));
                }
            } catch {
                /* best effort */
            }
            await Promise.race([Promise.all(jobs), new Promise((resolve) => setTimeout(resolve, 700))]);
        }
        async function leaveTo(url) {
            await purge();
            window.location.replace(url);
        }
        function goLocked(next) {
            state = next;
            leaveTo(next === "pending_approval" ? "/dwo/session/waiting" : "/dwo/session/locked");
        }

        // -- session ended: dialog, then the login page, then back to this screen ---------------------------
        function onExpired(reason, fromChannel) {
            if (state === "expired") {
                return;
            }
            state = "expired";
            if (channel && !fromChannel) {
                channel.postMessage({ type: "expired", reason });
            }
            const style = document.createElement("style");
            style.textContent = ".o_web_client > :not(.o-main-components-container){display:none!important}";
            document.head.appendChild(style);
            const here = location.pathname + location.search + location.hash;
            const back = () => {
                window.location.href = "/dwo/session/relogin?r=" + encodeURIComponent(here);
            };
            const why =
                {
                    idle: _t("You were inactive for too long."),
                    absolute: _t("The maximum duration of the session was reached."),
                    browser_closed: _t("The browser was closed."),
                    forced: _t("An administrator closed the session."),
                    pin_failed: _t("Too many wrong PINs."),
                }[reason] || "";
            dialog.add(
                ConfirmationDialog,
                {
                    title: _t("Session ended"),
                    body: _t("Your session has ended. %(why)s Sign in again to go back to the screen you were on.", {
                        why,
                    }),
                    confirmLabel: _t("Sign in again"),
                    confirm: back,
                    dismiss: back,
                },
                { onClose: back }
            );
        }

        // -- warning before the end of the session --------------------------------------------------------
        function closeToast() {
            if (toastClose) {
                toastClose();
                toastClose = null;
            }
            toastMinute = null;
        }
        function showWarning(left) {
            const minutes = Math.max(1, Math.ceil(left / 60));
            if (toastMinute === minutes) {
                return;
            }
            closeToast();
            toastMinute = minutes;
            const buttons = [];
            if (cfg.extend) {
                buttons.push({
                    name: _t("Extend"),
                    primary: true,
                    onClick: async () => {
                        const res = await post("/dwo/session/extend");
                        if (res && res.extended) {
                            warned = false;
                            closeToast();
                            handle(res);
                        }
                    },
                });
            }
            toastClose = notification.add(
                _t("Your session ends in about %(minutes)s minute(s). Save your work.", { minutes }),
                { type: "warning", sticky: true, title: _t("Session ending soon"), buttons }
            );
            warned = true;
        }
        function handle(res) {
            if (!res) {
                return;
            }
            cfg = res;
            if (res.state === "expired") {
                return onExpired(res.reason);
            }
            if (res.state !== "active") {
                return goLocked(res.state);
            }
            if (res.expires_in !== null && res.warn && res.expires_in <= res.warn) {
                showWarning(res.expires_in);
            } else if (warned) {
                warned = false;
                closeToast();
            }
        }

        // -- lock -------------------------------------------------------------------------------------------
        async function trySave() {
            try {
                const callbacks = [];
                env.bus.trigger("CLEAR-UNCOMMITTED-CHANGES", callbacks);
                await Promise.race([
                    Promise.all(callbacks.map((fn) => fn())),
                    new Promise((resolve) => setTimeout(resolve, 4000)),
                ]);
            } catch {
                /* a form that cannot be saved is lost */
            }
        }
        async function lock(reason) {
            if (state !== "active" || locking) {
                return;
            }
            if (cfg && !cfg.can_lock) {
                notification.add(_t("Set a PIN in your Preferences (Security tab) to lock the screen."), {
                    type: "info",
                });
                return;
            }
            locking = true;
            try {
                if (cfg && cfg.save_before_lock) {
                    await trySave();
                }
                const url = location.pathname + location.search + location.hash;
                const res = await post("/dwo/session/lock", { url, reason });
                if (res && res.state === "locked") {
                    if (channel) {
                        channel.postMessage({ type: "lock" });
                    }
                    goLocked("locked");
                } else {
                    handle(res);
                }
            } finally {
                locking = false;
            }
        }

        // -- heartbeat and idle detection ---------------------------------------------------------------------
        async function beat() {
            if (state !== "active") {
                return;
            }
            try {
                const idle = Math.floor((Date.now() - lastInput) / 1000);
                handle(await post("/dwo/session/heartbeat", { tab, idle }));
            } catch {
                /* offline: try again later */
            }
        }
        function onInput() {
            const now = Date.now();
            lastInput = now;
            if (channel && now - lastShared > 5000) {
                lastShared = now;
                channel.postMessage({ type: "activity" });
            }
        }
        for (const name of INPUT_EVENTS) {
            window.addEventListener(name, onInput, { passive: true, capture: true });
        }
        if (channel) {
            channel.onmessage = (ev) => {
                const type = ev.data && ev.data.type;
                if (type === "activity") {
                    lastInput = Date.now();
                } else if (type === "lock" && state === "active") {
                    goLocked("locked");
                } else if (type === "expired") {
                    onExpired(ev.data.reason, true);
                }
            };
        }
        window.addEventListener("pageshow", (ev) => {
            if (ev.persisted) {
                window.location.reload();
            }
        });
        window.addEventListener("pagehide", (ev) => {
            if (!ev.persisted && navigator.sendBeacon) {
                try {
                    navigator.sendBeacon(
                        "/dwo/session/bye",
                        new Blob([JSON.stringify({ jsonrpc: "2.0", method: "call", params: { tab } })], {
                            type: "application/json",
                        })
                    );
                } catch {
                    /* best effort */
                }
            }
        });
        setInterval(beat, 30000);
        setInterval(() => {
            if (state === "active" && cfg && cfg.lock_after && Date.now() - lastInput >= cfg.lock_after * 1000) {
                lock("idle");
            }
        }, 1000);
        // the heartbeat of the first minute is quicker, so the settings reach the page soon
        setTimeout(beat, 300);

        return { lock, beat, get state() { return state; }, get config() { return cfg; } };
    },
};

registry.category("services").add("dwo_session", dwoSessionService);

registry.category("user_menuitems").add(
    "dwo_lock_screen",
    (env) => ({
        type: "item",
        id: "dwo_lock_screen",
        description: _t("Lock screen"),
        callback: () => env.services.dwo_session.lock("manual"),
        sequence: 5,
    }),
    { sequence: 5 }
);
