/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

async function callKw(model, method, args) {
    const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: 1, params: { model, method, args, kwargs: {} } }),
    });
    const data = await response.json();
    if (data.error) {
        throw new Error(JSON.stringify(data.error.data || data.error));
    }
    return data.result;
}
const service = () => odoo.__WOWL_DEBUG__.root.env.services.dwo_session;

// The session ends while the user is on a screen: a dialog, then the login page, then the same screen again
registry.category("web_tour.tours").add("dwo_session_expiry_tour", {
    steps: () => [
        { content: "The web client is up", trigger: ".o_list_renderer" },
        {
            content: "An administrator closes the session (here: our own)",
            trigger: ".o_list_renderer",
            async run() {
                const ids = await callKw("dwo.session", "search", [[["state", "=", "active"]]]);
                await callKw("dwo.session", "action_force_logout", [ids]);
                await service().beat();
            },
        },
        { content: "The dialog says the session ended", trigger: ".modal-title:contains('Session ended')" },
        { content: "The screen behind it is hidden", trigger: "body", run() {
            if (document.querySelector(".o_list_renderer") && getComputedStyle(document.querySelector(".o_action_manager")).display !== "none") {
                throw new Error("the web client is still visible behind the dialog");
            }
        } },
        { content: "Sign in again", trigger: ".modal-footer .btn-primary:contains('Sign in again')", run: "click", expectUnloadPage: true },
        { content: "The login page, asking for the password again", trigger: "input[name=login]", run: "edit admin" },
        { trigger: "input[name=password]", run: "edit admin" },
        { trigger: "button[type=submit]", run: "click", expectUnloadPage: true },
        {
            content: "Back on the same screen",
            trigger: ".o_list_renderer",
            run() {
                if (location.pathname !== "/odoo/users") {
                    throw new Error("not back on the screen: " + location.pathname);
                }
            },
        },
    ],
});

// The warning before the end of the session, with an Extend button that removes it
registry.category("web_tour.tours").add("dwo_session_toast_tour", {
    steps: () => [
        { content: "The web client is up", trigger: ".o_list_renderer" },
        {
            content: "The session ends in a minute (setting of the administrator)",
            trigger: ".o_list_renderer",
            async run() {
                await callKw("ir.config_parameter", "set_param", ["dwo_session.absolute_min", "1"]);
                await service().beat();
            },
        },
        { content: "The warning appears", trigger: ".o_notification:contains('Your session ends in about')" },
        { content: "It has an Extend button", trigger: ".o_notification button:contains('Extend')", run: "click" },
        { content: "The warning goes away", trigger: "body:not(:has(.o_notification:contains('Your session ends in about')))" },
    ],
});
