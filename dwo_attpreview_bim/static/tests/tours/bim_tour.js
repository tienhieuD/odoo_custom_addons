/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Odoo 17: tours are added through dwoAddTour (see dwo_attpreview_core/static/tests/tours/tour_compat.js)
import { dwoAddTour } from "@dwo_attpreview_core/../tests/tours/tour_compat";

dwoAddTour("dwo_attpreview_bim_tour", {
    steps: () => [
        { trigger: ".o_field_widget[name=datas] .o_dwo_ap_field_preview", run: "click" },
        { trigger: ".o_dwo_ap_dialog .o_dwo_webgl" },
        // WebGL may be missing in a headless test browser: then the dialog shows a clear message instead of a model
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl[data-state=error] .o_dwo_webgl_error", timeout: 60000 },
        { trigger: ".o_dwo_webgl[data-state=ready], .o_dwo_webgl_download" },
    ],
});
