// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Sandboxed 3D viewer page: the parent sends the bytes of the file (postMessage), three.js loaders parse them here.
import { THREE, bridge, createStage, formatStats } from "/dwo_attpreview_webgl/asset/viewer/common.js";
import { STLLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/STLLoader.js";
import { OBJLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/OBJLoader.js";
import { PLYLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/PLYLoader.js";
import { GLTFLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/GLTFLoader.js";
import { ThreeMFLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/3MFLoader.js";
import { FBXLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/FBXLoader.js";
import { ColladaLoader } from "/dwo_attpreview_webgl/asset/lib/three/examples/jsm/loaders/ColladaLoader.js";

// the stage is made when the file arrives: a browser without WebGL then gets a clear message, not an endless spinner
let stage = null;
function getStage() {
    if (!stage) {
        stage = createStage(document.getElementById("stage"));
        stage.wireButton();
    }
    return stage;
}
// CAD and print files are Z-up; the viewer is Y-up
const Z_UP = ["stl", "ply", "3mf"];

function material(geometry) {
    const colored = !!geometry.attributes.color;
    return new THREE.MeshStandardMaterial({
        color: colored ? 0xffffff : 0x9aa7b8, vertexColors: colored, metalness: 0.1, roughness: 0.6, side: THREE.DoubleSide,
    });
}

function meshOf(geometry) {
    if (!geometry.attributes.normal) {
        geometry.computeVertexNormals();
    }
    return new THREE.Mesh(geometry, material(geometry));
}

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

function defaults(object) {
    object.traverse((o) => {
        if (o.isMesh && (!o.material || (Array.isArray(o.material) && !o.material.length))) {
            o.material = material(o.geometry);
        }
        if (o.isMesh && o.material && !Array.isArray(o.material)) {
            o.material.side = THREE.DoubleSide;
        }
    });
}

bridge("dwo_attpreview_3d", async (kind, buffer) => {
    const load = LOADERS[kind];
    if (!load) {
        throw new Error("Unsupported file type: " + kind);
    }
    getStage();
    const object = await load(buffer);
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
});
