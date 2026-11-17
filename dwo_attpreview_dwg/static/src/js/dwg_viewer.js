/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
import { registry } from "@web/core/registry";
import { DwoWebglViewer } from "@dwo_attpreview_webgl/js/webgl_viewer";

/** Viewer of the "dwg" engine: DWG drawings. */
export class DwgViewer extends DwoWebglViewer {
    static config = {
        viewerUrl: "/dwo_attpreview_dwg/asset/viewer/viewer.html",
        source: "dwo_attpreview_dwg",
        fileUrl: (id) => `/dwo_attpreview_dwg/file/${id}`,
    };
}

registry.category("dwo_attpreview.viewers").add("dwg", DwgViewer);
