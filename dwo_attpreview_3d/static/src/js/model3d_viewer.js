/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { DwoWebglViewer } from "@dwo_attpreview_webgl/js/webgl_viewer";

/** Viewer of the "model3d" engine: STL, OBJ, GLB, GLTF, 3MF, PLY, FBX, DAE, STEP, IGES, 3DM. */
export class Model3DViewer extends DwoWebglViewer {
    static config = {
        // STEP, IGES and 3DM are read by WebAssembly modules that build functions with new Function: they have their
        // own page (and CSP); every other format keeps the stricter page
        viewerUrl: (kind) => `/dwo_attpreview_3d/asset/viewer/${["step", "stp", "iges", "igs", "3dm"].includes(kind) ? "solid" : "viewer"}.html`,
        source: "dwo_attpreview_3d",
        fileUrl: (id) => `/dwo_attpreview_3d/file/${id}`,
    };
}

registry.category("dwo_attpreview.viewers").add("model3d", Model3DViewer);
