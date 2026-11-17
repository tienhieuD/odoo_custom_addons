// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Sandboxed BIM viewer page: the parent sends the bytes of the IFC file (postMessage); web-ifc (WebAssembly) reads
// them here and three.js draws the geometry. Properties come from the same reader. Nothing leaves this page.
import { THREE, bridge, createStage, formatStats } from "/dwo_attpreview_webgl/asset/viewer/common.js";
import * as WebIFC from "/dwo_attpreview_bim/asset/lib/web-ifc/web-ifc-api.js";

const SPATIAL = new Set(["IFCPROJECT", "IFCSITE", "IFCBUILDING", "IFCBUILDINGSTOREY"]);
const treeEl = document.getElementById("tree");
const propsEl = document.getElementById("props");
let stage = null;
let api = null;
let modelID = -1;
const parts = []; // {mesh, ids (expressID of each vertex), index (all triangles, Uint32Array), position}
const hidden = new Set();
let highlight = null;

function getStage() {
    if (!stage) {
        stage = createStage(document.getElementById("stage"));
        stage.wireButton();
        const bar = document.getElementById("bar");
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.id = "tree-toggle";
        toggle.textContent = "Structure";
        toggle.title = "Show or hide the building structure";
        toggle.addEventListener("click", () => {
            treeEl.hidden = !treeEl.hidden;
            toggle.classList.toggle("on", !treeEl.hidden);
        });
        bar.insertBefore(toggle, bar.children[1]);
    }
    return stage;
}

// --- geometry --------------------------------------------------------------------------------------------------
function buildGeometry() {
    const groups = new Map(); // colour key -> arrays
    api.StreamAllMeshes(modelID, (flat) => {
        const placed = flat.geometries;
        for (let i = 0; i < placed.size(); i++) {
            const g = placed.get(i);
            const geom = api.GetGeometry(modelID, g.geometryExpressID);
            const vertices = api.GetVertexArray(geom.GetVertexData(), geom.GetVertexDataSize());
            const indices = api.GetIndexArray(geom.GetIndexData(), geom.GetIndexDataSize());
            const c = g.color;
            const key = [c.x, c.y, c.z, c.w].map((v) => v.toFixed(3)).join(",");
            let group = groups.get(key);
            if (!group) {
                group = { color: c, position: [], normal: [], ids: [], index: [] };
                groups.set(key, group);
            }
            const matrix = new THREE.Matrix4().fromArray(g.flatTransformation);
            const normalMatrix = new THREE.Matrix3().getNormalMatrix(matrix);
            const base = group.position.length / 3;
            const v = new THREE.Vector3();
            for (let k = 0; k < vertices.length; k += 6) {
                v.set(vertices[k], vertices[k + 1], vertices[k + 2]).applyMatrix4(matrix);
                group.position.push(v.x, v.y, v.z);
                v.set(vertices[k + 3], vertices[k + 4], vertices[k + 5]).applyMatrix3(normalMatrix).normalize();
                group.normal.push(v.x, v.y, v.z);
                group.ids.push(flat.expressID);
            }
            for (let k = 0; k < indices.length; k++) {
                group.index.push(indices[k] + base);
            }
            geom.delete();
        }
    });
    for (const group of groups.values()) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(group.position, 3));
        geometry.setAttribute("normal", new THREE.Float32BufferAttribute(group.normal, 3));
        const index = Uint32Array.from(group.index);
        geometry.setIndex(new THREE.BufferAttribute(index.slice(), 1));
        const c = group.color;
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color(c.x, c.y, c.z), opacity: c.w, transparent: c.w < 1, side: THREE.DoubleSide,
            metalness: 0.05, roughness: 0.8, depthWrite: c.w >= 1,
        });
        const mesh = new THREE.Mesh(geometry, material);
        stage.content.add(mesh);
        parts.push({ mesh, ids: Uint32Array.from(group.ids), index });
    }
}

/** Rebuild the index of each mesh without the triangles of hidden elements. */
function applyVisibility() {
    for (const part of parts) {
        if (!hidden.size) {
            part.mesh.geometry.setIndex(new THREE.BufferAttribute(part.index.slice(), 1));
            continue;
        }
        const kept = [];
        for (let t = 0; t < part.index.length; t += 3) {
            if (!hidden.has(part.ids[part.index[t]])) {
                kept.push(part.index[t], part.index[t + 1], part.index[t + 2]);
            }
        }
        part.mesh.geometry.setIndex(new THREE.BufferAttribute(Uint32Array.from(kept), 1));
    }
    clearSelection();
    stage.setWireframe(stage.wire);
}

// --- selection and properties ------------------------------------------------------------------------------------
function clearSelection() {
    if (highlight) {
        stage.content.remove(highlight);
        highlight.geometry.dispose();
        highlight = null;
    }
    propsEl.hidden = true;
    propsEl.textContent = "";
    stage.setWireframe(stage.wire);
}

function select(expressID) {
    if (highlight) {
        stage.content.remove(highlight);
        highlight.geometry.dispose();
        highlight = null;
    }
    const position = [];
    for (const part of parts) {
        const src = part.mesh.geometry.attributes.position;
        for (let t = 0; t < part.index.length; t += 3) {
            if (part.ids[part.index[t]] === expressID) {
                for (let k = 0; k < 3; k++) {
                    position.push(src.getX(part.index[t + k]), src.getY(part.index[t + k]), src.getZ(part.index[t + k]));
                }
            }
        }
    }
    if (position.length) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(position, 3));
        geometry.computeVertexNormals();
        highlight = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color: 0xffb020, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
        stage.content.add(highlight);
    }
    showProperties(expressID);
    stage.setWireframe(stage.wire);
}

const val = (x) => (x && typeof x === "object" && "value" in x ? x.value : x);

function row(table, name, value) {
    if (value === undefined || value === null || value === "") {
        return;
    }
    const tr = table.insertRow();
    tr.insertCell().textContent = String(name);
    tr.insertCell().textContent = String(value);
}

async function showProperties(expressID) {
    propsEl.hidden = false;
    propsEl.textContent = "";
    const title = document.createElement("h3");
    propsEl.appendChild(title);
    try {
        const item = await api.properties.getItemProperties(modelID, expressID, false);
        title.textContent = val(item.Name) || api.GetNameFromTypeCode(item.type);
        const main = document.createElement("table");
        row(main, "Type", api.GetNameFromTypeCode(item.type));
        row(main, "GlobalId", val(item.GlobalId));
        row(main, "Description", val(item.Description));
        row(main, "Express ID", expressID);
        propsEl.appendChild(main);
        const psets = (await api.properties.getPropertySets(modelID, expressID, true)) || [];
        for (const pset of psets) {
            const h = document.createElement("h4");
            h.textContent = val(pset.Name) || "Properties";
            const table = document.createElement("table");
            for (const p of pset.HasProperties || pset.Quantities || []) {
                row(table, val(p.Name), val(p.NominalValue) ?? val(p.LengthValue) ?? val(p.AreaValue) ?? val(p.VolumeValue) ?? val(p.CountValue) ?? val(p.WeightValue));
            }
            propsEl.append(h, table);
        }
    } catch (e) {
        title.textContent = "Element " + expressID;
        const hint = document.createElement("p");
        hint.className = "hint";
        hint.textContent = "Properties could not be read.";
        propsEl.appendChild(hint);
    }
}

function pick(ev) {
    const canvas = stage.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    const ndc = new THREE.Vector2(((ev.clientX - rect.left) / rect.width) * 2 - 1, -((ev.clientY - rect.top) / rect.height) * 2 + 1);
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, stage.camera);
    const hits = ray.intersectObjects(parts.map((p) => p.mesh), false);
    if (!hits.length) {
        clearSelection();
        return;
    }
    const hit = hits[0];
    const part = parts.find((p) => p.mesh === hit.object);
    select(part.ids[hit.face.a]);
}

// --- structure tree -----------------------------------------------------------------------------------------------
async function elementsUnder(node, into) {
    for (const child of node.children || []) {
        into.add(child.expressID);
        await elementsUnder(child, into);
    }
    return into;
}

async function buildTree() {
    const root = await api.properties.getSpatialStructure(modelID);
    const ul = document.createElement("ul");
    let storeys = 0;
    async function add(node, parent) {
        const type = (typeof node.type === "string" ? node.type : api.GetNameFromTypeCode(node.type)).toUpperCase();
        if (!SPATIAL.has(type)) {
            return;
        }
        const li = document.createElement("li");
        const label = document.createElement("label");
        const box = document.createElement("input");
        box.type = "checkbox";
        box.checked = true;
        const ids = await elementsUnder(node, new Set([node.expressID]));
        box.addEventListener("change", () => {
            for (const id of ids) {
                box.checked ? hidden.delete(id) : hidden.add(id);
            }
            applyVisibility();
        });
        const name = document.createElement("span");
        let text = type.replace("IFC", "").toLowerCase();
        try {
            const item = await api.properties.getItemProperties(modelID, node.expressID, false);
            text = val(item.Name) || text;
        } catch (e) {
            /* the type is shown */
        }
        name.textContent = text;
        const kind = document.createElement("span");
        kind.className = "kind";
        kind.textContent = type.replace("IFC", "").toLowerCase();
        label.append(box, name, kind);
        li.appendChild(label);
        parent.appendChild(li);
        if (type === "IFCBUILDINGSTOREY") {
            storeys++;
        }
        const sub = document.createElement("ul");
        for (const child of node.children || []) {
            await add(child, sub);
        }
        if (sub.children.length) {
            li.appendChild(sub);
        }
    }
    await add(root, ul);
    treeEl.textContent = "";
    treeEl.appendChild(ul);
    treeEl.hidden = !ul.children.length;
    document.getElementById("tree-toggle")?.classList.toggle("on", !treeEl.hidden);
    return storeys;
}

/**
 * Box of the building: the elements far from the others (a survey point, a grid, a misplaced object) are left out, so the
 * view is not zoomed out to show them. The tail is cut at three times the 75th percentile of the distances to the median.
 */
function mainBox() {
    const boxes = new Map();
    for (const part of parts) {
        const pos = part.mesh.geometry.attributes.position;
        for (let i = 0; i < pos.count; i++) {
            const id = part.ids[i];
            let b = boxes.get(id);
            if (!b) {
                b = new THREE.Box3();
                boxes.set(id, b);
            }
            b.expandByPoint(new THREE.Vector3().fromBufferAttribute(pos, i));
        }
    }
    const items = [...boxes.values()].map((b) => ({ b, c: b.getCenter(new THREE.Vector3()) }));
    const all = new THREE.Box3();
    items.forEach((it) => all.union(it.b));
    if (items.length < 4) {
        return all;
    }
    const median = (axis) => items.map((it) => it.c[axis]).sort((a, b) => a - b)[items.length >> 1];
    const mid = new THREE.Vector3(median("x"), median("y"), median("z"));
    const dist = items.map((it) => it.c.distanceTo(mid)).sort((a, b) => a - b);
    const limit = Math.max(dist[Math.floor(dist.length * 0.75)] * 3, 1e-6);
    const kept = new THREE.Box3();
    items.forEach((it) => it.c.distanceTo(mid) <= limit && kept.union(it.b));
    return kept.isEmpty() ? all : kept;
}

// --- load -----------------------------------------------------------------------------------------------------------
bridge("dwo_attpreview_bim", async (kind, buffer) => {
    getStage();
    api = new WebIFC.IfcAPI();
    api.SetWasmPath("/dwo_attpreview_bim/asset/lib/web-ifc/", true);
    await api.Init();
    modelID = api.OpenModel(new Uint8Array(buffer), { COORDINATE_TO_ORIGIN: true });
    if (modelID < 0) {
        throw new Error("This IFC file could not be read.");
    }
    buildGeometry();
    if (!parts.length) {
        throw new Error("The model contains no geometry to show.");
    }
    // web-ifc already gives Y-up coordinates (the IFC Z axis is mapped to Y), no rotation is needed
    stage.content.updateMatrixWorld(true);
    stage.fitBox = mainBox();
    stage.fit();
    const storeys = await buildTree();
    stage.renderer.domElement.addEventListener("click", (ev) => {
        if (!stage.dragged) {
            pick(ev);
        }
    });
    // a click that ends a drag (orbit) must not select
    let down = null;
    stage.renderer.domElement.addEventListener("pointerdown", (ev) => { down = [ev.clientX, ev.clientY]; stage.dragged = false; });
    stage.renderer.domElement.addEventListener("pointermove", (ev) => { if (down && Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) > 4) stage.dragged = true; });
    const stats = stage.stats();
    stage.setInfo(formatStats(stats) + `, ${storeys} storeys`);
    return Object.assign(stats, { storeys, elements: new Set(parts.flatMap((p) => Array.from(p.ids))).size });
});
