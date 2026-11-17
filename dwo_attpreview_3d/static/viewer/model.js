// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Shared by the pages of the 3D viewer: the stage, default materials and the common way to show a loaded object.
import { THREE, createStage, formatStats } from "/dwo_attpreview_webgl/asset/viewer/common.js";

// the stage is made when the file arrives: a browser without WebGL then gets a clear message, not an endless spinner
let stage = null;
export function getStage() {
    if (!stage) {
        stage = createStage(document.getElementById("stage"));
        stage.wireButton();
    }
    return stage;
}
// CAD and print files are Z-up; the viewer is Y-up
export const Z_UP = ["stl", "ply", "3mf", "step", "stp", "iges", "igs", "3dm"];

export function material(geometry) {
    const colored = !!geometry.attributes.color;
    return new THREE.MeshStandardMaterial({
        color: colored ? 0xffffff : 0x9aa7b8, vertexColors: colored, metalness: 0.1, roughness: 0.6, side: THREE.DoubleSide,
    });
}

export function meshOf(geometry) {
    if (!geometry.attributes.normal) {
        geometry.computeVertexNormals();
    }
    return new THREE.Mesh(geometry, material(geometry));
}



export function defaults(object) {
    object.traverse((o) => {
        if (o.isMesh && (!o.material || (Array.isArray(o.material) && !o.material.length))) {
            o.material = material(o.geometry);
        }
        if (o.isMesh && o.material) {
            for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
                m.side = THREE.DoubleSide;
                // a texture kept in a separate file is never loaded (no network), and a pure black colour (the default
                // of some CAD files) shows nothing but a silhouette: both get the neutral colour
                if (m.map && !m.map.image) {
                    m.map = null;
                }
                if (!m.map && !m.vertexColors && m.color && m.color.r + m.color.g + m.color.b < 0.03) {
                    m.color.set(0x9aa7b8);
                }
            }
        }
    });
}

/** Put a loaded object in the stage, fit the view and return the statistics (shown in the toolbar too). */
export function show(object, kind) {
    if (!object) {
        throw new Error("The file contains nothing to show.");
    }
    defaults(object);
    if (Z_UP.includes(kind)) {
        object.rotation.x = -Math.PI / 2;
    }
    stage.content.add(object);
    stage.content.updateMatrixWorld(true);
    stage.fit();
    const stats = stage.stats();
    if (!stats.objects) {
        throw new Error("The file contains nothing to show.");
    }
    stage.setInfo(formatStats(stats));
    return stats;
}
