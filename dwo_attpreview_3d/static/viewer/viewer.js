// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Sandboxed 3D viewer page: the parent sends the bytes of the file (postMessage), three.js loaders parse them here.
// STEP, IGES and 3DM (WebAssembly readers) are in solid.html: only that page may use unsafe-eval.
import { THREE, bridge } from "/dwo_attpreview_webgl/asset/viewer/common.js";
import { getStage, meshOf, show } from "./model.js";
import { STLLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/STLLoader.js";
import { OBJLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/OBJLoader.js";
import { PLYLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/PLYLoader.js";
import { GLTFLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/GLTFLoader.js";
import { ThreeMFLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/3MFLoader.js";
import { FBXLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/FBXLoader.js";
import { ColladaLoader } from "/dwo_attpreview_webgl/asset/lib/dGhyZWU/examples/jsm/loaders/ColladaLoader.js";

const text = (buffer) => new TextDecoder("utf-8").decode(buffer);

const LOADERS = {
    stl: (buffer) => meshOf(new STLLoader().parse(buffer)),
    ply: (buffer) => {
        const geometry = new PLYLoader().parse(buffer);
        if (!geometry.index && geometry.attributes.position.count && !geometry.attributes.normal) {
            // no faces: a point cloud
            const colored = !!geometry.attributes.color;
            return new THREE.Points(geometry, new THREE.PointsMaterial({ size: 0.01, vertexColors: colored, color: colored ? 0xffffff : 0x4a5568, sizeAttenuation: true }));
        }
        return meshOf(geometry);
    },
    obj: (buffer) => new OBJLoader().parse(text(buffer)),
    glb: (buffer) => new Promise((ok, no) => new GLTFLoader().parse(buffer, "", (g) => ok(g.scene), no)),
    gltf: (buffer) => new Promise((ok, no) => new GLTFLoader().parse(buffer, "", (g) => ok(g.scene), no)),
    "3mf": (buffer) => new ThreeMFLoader().parse(buffer),
    fbx: (buffer) => new FBXLoader().parse(buffer, ""),
    dae: (buffer) => new ColladaLoader().parse(text(buffer), "").scene,
};

bridge("dwo_attpreview_3d", async (kind, buffer) => {
    const load = LOADERS[kind];
    if (!load) {
        throw new Error("Unsupported file type: " + kind);
    }
    getStage();
    return show(await load(buffer), kind);
});
