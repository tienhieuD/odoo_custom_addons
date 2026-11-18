/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// Signs in through the themed login page: the form of Odoo must still work with every layout.
registry.category("web_tour.tours").add("dwo_login_themes_tour", {
    steps: () => [
        { content: "The themed page is shown", trigger: ".container.dwo_lc .dwo_bg" },
        { content: "The form is visible", trigger: ".dwo_lc form.oe_login_form input[name=login]" },
        { content: "Type the login", trigger: "input[name=login]", run: "text admin" },
        { content: "Type the password", trigger: "input[name=password]", run: "text admin" },
        { content: "Log in", trigger: ".oe_login_buttons button[type=submit]", run: "click" },
        { content: "The web client is open", trigger: ".o_main_navbar" },
    ],
});
