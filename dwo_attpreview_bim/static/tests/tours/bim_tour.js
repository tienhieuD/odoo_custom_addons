/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Odoo 20: the file field of an attachment is called raw (datas before)
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("dwo_attpreview_bim_tour", {
    steps: () => [
        { trigger: ".o_field_widget[name=raw] .o_dwo_ap_field_preview", run: "click" },
        { trigger: ".o_dwo_ap_dialog .o_dwo_webgl iframe" },
        // WebGL may be missing in a headless test browser: then the dialog shows a clear message instead of a model
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl[data-state=error] .o_dwo_webgl_error", timeout: 60000 },
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl_download" },
    ],
});
