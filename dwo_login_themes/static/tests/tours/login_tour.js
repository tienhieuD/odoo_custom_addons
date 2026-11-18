/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// Signs in through the themed login page: the form of Odoo must still work with every layout.
registry.category("web_tour.tours").add("dwo_login_themes_tour", {
    steps: () => [
        { content: "The themed page is shown", trigger: ".container.dwo_lc .dwo_bg" },
        { content: "The form is visible", trigger: ".dwo_lc form.oe_login_form input[name=login]" },
        { content: "Top bar: the fields and the Log in button end on the same line", trigger: ".dwo_lc form.oe_login_form input[name=login]", run: () => {
            // only the top bar, and only when the window is wide enough for one row
            if (!document.querySelector(".container.dwo_l_topbar") || window.innerWidth < 1100) { return; }
            const bottom = (sel) => document.querySelector(sel).getBoundingClientRect().bottom;
            const mail = bottom("input[name=login]");
            const button = document.querySelector(".oe_login_buttons button[type=submit]").getBoundingClientRect();
            if (Math.abs(mail - bottom("input[name=password]")) > 1) { throw new Error("Top bar: Email and Password are not aligned"); }
            if (button.top < mail && Math.abs(mail - button.bottom) > 1) { throw new Error("Top bar: the Log in button is not aligned with the fields"); }
        } },
        { content: "Type the login", trigger: "input[name=login]", run: "edit admin" },
        { content: "Type the password", trigger: "input[name=password]", run: "edit admin" },
        { content: "Log in", trigger: ".oe_login_buttons button[type=submit]", run: "click", expectUnloadPage: true },
        { content: "The web client is open", trigger: ".o_main_navbar" },
    ],
});

// "Powered by Odoo": hidden (class added by login_theme.js) when the option is on, still shown when it is off.
registry.category("web_tour.tours").add("dwo_login_themes_brand_hidden_tour", {
    steps: () => [
        { content: "The form is visible", trigger: "form.oe_login_form input[name=login]" },
        { content: "The brand link got the hiding class", trigger: "body:has(a[href*='odoo.com'].dwo_brand_off)" },
    ],
});
registry.category("web_tour.tours").add("dwo_login_themes_brand_shown_tour", {
    steps: () => [
        { content: "The form is visible", trigger: "form.oe_login_form input[name=login]" },
        { content: "The brand link is shown", trigger: "a[href*='odoo.com']:contains('Powered by')" },
        { content: "Nothing was hidden", trigger: "body:not(:has(.dwo_brand_off))" },
    ],
});
