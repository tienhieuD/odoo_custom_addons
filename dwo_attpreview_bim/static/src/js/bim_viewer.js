/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { DwoWebglViewer } from "@dwo_attpreview_webgl/js/webgl_viewer";

/** Viewer of the "bim" engine: IFC building models. */
export class BimViewer extends DwoWebglViewer {
    static config = {
        viewerUrl: "/dwo_attpreview_bim/asset/viewer/viewer.html",
        source: "dwo_attpreview_bim",
        fileUrl: (id) => `/dwo_attpreview_bim/file/${id}`,
    };
}

registry.category("dwo_attpreview.viewers").add("bim", BimViewer);
