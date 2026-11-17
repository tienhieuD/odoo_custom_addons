// Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
// Sandboxed DWG viewer page: the parent sends the bytes of the file (postMessage), LibreDWG (WebAssembly) converts them
// to DXF here and dxf-viewer draws the result.
import { THREE, bridge, requireWebGL } from "/dwo_attpreview_webgl/asset/viewer/common.js";
import { DxfViewer } from "/dwo_attpreview_dwg/asset/lib/dxf-viewer/dxf-viewer.bundle.js";
import { LibreDwg } from "/dwo_attpreview_dwg/asset/lib/libredwg/dist/libredwg-web.js";

const FONTS = ["noto-sans-latin-400-normal.woff", "noto-sans-latin-ext-400-normal.woff", "noto-sans-vietnamese-400-normal.woff"]
    .map((name) => "/dwo_attpreview_dwg/asset/lib/dxf-viewer/fonts/" + name);
const stageEl = document.getElementById("stage");
const layersEl = document.getElementById("layers");
const info = document.getElementById("info");
let viewer = null;
let dark = false;

function fit() {
    const bounds = viewer.GetBounds();
    const origin = viewer.GetOrigin();
    if (bounds) {
        viewer.FitView(bounds.minX - origin.x, bounds.maxX - origin.x, bounds.minY - origin.y, bounds.maxY - origin.y, 0.08);
    }
}

function buildLayers() {
    layersEl.textContent = "";
    for (const layer of viewer.GetLayers(true)) {
        const label = document.createElement("label");
        const box = document.createElement("input");
        box.type = "checkbox";
        box.checked = true;
        box.addEventListener("change", () => viewer.ShowLayer(layer.name, box.checked));
        const swatch = document.createElement("span");
        swatch.className = "swatch";
        swatch.style.background = "#" + (layer.color >>> 0).toString(16).padStart(6, "0");
        label.append(box, swatch, document.createTextNode(layer.displayName || layer.name));
        layersEl.appendChild(label);
    }
    return layersEl.children.length;
}

document.getElementById("reset").addEventListener("click", () => viewer && fit());
document.getElementById("layers-open").addEventListener("click", (ev) => {
    layersEl.hidden = !layersEl.hidden;
    ev.currentTarget.setAttribute("aria-expanded", String(!layersEl.hidden));
});
document.getElementById("dark").addEventListener("click", (ev) => {
    dark = !dark;
    ev.currentTarget.classList.toggle("on", dark);
    ev.currentTarget.setAttribute("aria-pressed", String(dark));
    viewer.SetClearColor(dark ? "#20232a" : "#ffffff");
});

bridge("dwo_attpreview_dwg", async (kind, buffer) => {
    // the stage is made when the file arrives: a browser without WebGL then gets a clear message
    requireWebGL();
    viewer = new DxfViewer(stageEl, {
        autoResize: true, clearColor: new THREE.Color("#ffffff"), canvasAlpha: false, antialias: true,
        colorCorrection: true, blackWhiteInversion: true,
    });
    const libredwg = await LibreDwg.create();
    const dxf = libredwg.dwg_write_dxf(buffer);
    if (!dxf || !dxf.length) {
        throw new Error("This DWG file could not be read (it may be damaged or in a version that is not supported).");
    }
    const url = URL.createObjectURL(new Blob([dxf], { type: "application/octet-stream" }));
    try {
        await viewer.Load({ url, fonts: FONTS });
    } finally {
        URL.revokeObjectURL(url);
    }
    const layers = buildLayers();
    const bounds = viewer.GetBounds();
    if (!bounds) {
        throw new Error("The drawing contains nothing to show.");
    }
    fit();
    const size = [bounds.maxX - bounds.minX, bounds.maxY - bounds.minY].map((v) => Math.round(v * 100) / 100);
    info.textContent = `${layers} layers, ${size[0]} x ${size[1]}`;
    return { layers, size };
});
