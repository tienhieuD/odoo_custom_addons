/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { DwoWebglViewer } from "@dwo_attpreview_webgl/js/webgl_viewer";

/** Viewer of the "cad" engine: DXF drawings. */
export class CadViewer extends DwoWebglViewer {
    static config = {
        viewerUrl: "/dwo_attpreview_cad/asset/viewer/viewer.html",
        source: "dwo_attpreview_cad",
        fileUrl: (id) => `/dwo_attpreview_cad/file/${id}`,
    };
}

registry.category("dwo_attpreview.viewers").add("cad", CadViewer);
