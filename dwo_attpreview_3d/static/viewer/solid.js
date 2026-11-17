// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Sandboxed page of the solid-model readers built with WebAssembly: STEP and IGES (Open CASCADE meshes them) and Rhino 3DM
// (rhino3dm reads the meshes and the render meshes of breps saved in the file). three.js draws the result.
import { THREE, bridge } from "/dwo_attpreview_webgl/asset/viewer/common.js";
import { getStage, meshOf, show } from "./model.js";

const FALLBACK = 0x9aa7b8;

/** STEP / IGES: Open CASCADE gives meshes (positions, normals, index, colour); each one becomes a THREE mesh. */
async function loadCad(kind, buffer) {
    const { occtimportjs } = await import("/dwo_attpreview_3d/asset/lib/occt/occt-import-js.bundle.js");
    const occt = await occtimportjs({ locateFile: (name) => "/dwo_attpreview_3d/asset/lib/occt/" + name });
    const bytes = new Uint8Array(buffer);
    const result = kind === "iges" || kind === "igs" ? occt.ReadIgesFile(bytes, null) : occt.ReadStepFile(bytes, null);
    if (!result || !result.success || !result.meshes.length) {
        throw new Error("This file could not be read, or it contains no solid or surface to show.");
    }
    const group = new THREE.Group();
    for (const m of result.meshes) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(m.attributes.position.array, 3));
        if (m.attributes.normal) {
            geometry.setAttribute("normal", new THREE.Float32BufferAttribute(m.attributes.normal.array, 3));
        }
        geometry.setIndex(new THREE.BufferAttribute(Uint32Array.from(m.index.array), 1));
        const mesh = meshOf(geometry);
        if (m.color) {
            mesh.material.color.setRGB(m.color[0], m.color[1], m.color[2]);
        }
        group.add(mesh);
    }
    return group;
}

function toThree(rh, geometry) {
    const type = geometry.constructor.name;
    let mesh = null;
    if (type === "Mesh") {
        mesh = geometry;
    } else if (type === "Brep" || type === "Extrusion" || type === "SubD") {
        const joined = new rh.Mesh();
        const faces = type === "Brep" ? geometry.faces() : null;
        if (faces) {
            for (let i = 0; i < faces.count; i++) {
                const part = faces.get(i).getMesh(rh.MeshType.Any);
                if (part) {
                    joined.append(part);
                    part.delete();
                }
            }
        } else {
            const part = geometry.getMesh ? geometry.getMesh(rh.MeshType.Any) : null;
            if (part) {
                joined.append(part);
                part.delete();
            }
        }
        mesh = joined;
    }
    if (!mesh || !mesh.vertices().count) {
        return null;
    }
    const loaded = new THREE.BufferGeometryLoader().parse(mesh.toThreejsJSON());
    if (!loaded.attributes.normal) {
        loaded.computeVertexNormals();
    }
    return loaded;
}

async function loadRhino(buffer) {
    const { default: rhino3dm } = await import("/dwo_attpreview_3d/asset/lib/rhino3dm/rhino3dm.module.min.js");
    const rh = await rhino3dm({ locateFile: (name) => "/dwo_attpreview_3d/asset/lib/rhino3dm/" + name });
    const doc = rh.File3dm.fromByteArray(new Uint8Array(buffer));
    if (!doc) {
        throw new Error("This 3DM file could not be read (it may be damaged or saved by a newer version of Rhino).");
    }
    const group = new THREE.Group();
    const objects = doc.objects();
    for (let i = 0; i < objects.count; i++) {
        const object = objects.get(i);
        const geometry = toThree(rh, object.geometry());
        if (!geometry) {
            continue;
        }
        const color = object.attributes().drawColor(doc);
        const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
            color: color && (color.r || color.g || color.b) ? new THREE.Color(color.r / 255, color.g / 255, color.b / 255) : FALLBACK,
            metalness: 0.1, roughness: 0.6, side: THREE.DoubleSide,
        }));
        group.add(mesh);
    }
    if (!group.children.length) {
        throw new Error("The file contains no mesh, brep or extrusion to show.");
    }
    return group;
}

bridge("dwo_attpreview_3d", async (kind, buffer) => {
    getStage();
    return show(await (kind === "3dm" ? loadRhino(buffer) : loadCad(kind === "stp" ? "step" : kind === "igs" ? "iges" : kind, buffer)), kind);
});
