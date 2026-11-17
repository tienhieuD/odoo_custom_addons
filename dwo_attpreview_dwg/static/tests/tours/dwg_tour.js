/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("dwo_attpreview_dwg_tour", {
    steps: () => [
        { trigger: ".o_field_widget[name=datas] .o_dwo_ap_field_preview", run: "click" },
        { trigger: ".o_dwo_ap_dialog .o_dwo_webgl" },
        // WebGL may be missing in a headless test browser: then the dialog shows a clear message instead of a model
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl[data-state=error] .o_dwo_webgl_error", timeout: 60000 },
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl_download" },
    ],
});
