// Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// Shared code of the sandboxed 3D viewer pages (iframe sandbox="allow-scripts", opaque origin, CSP without network).
// The parent window sends the file bytes with postMessage; nothing is fetched from anywhere else.
import * as THREE from "../lib/dGhyZWU/build/three.module.js";
import { OrbitControls } from "../lib/dGhyZWU/examples/jsm/controls/OrbitControls.js";

export { THREE };

/**
 * Messages: the page sends {source: SOURCE, type: "ready" | "rendered" | "error", ...}; the parent answers
 * {source: SOURCE + "_parent", type: "load", kind, buffer}. ``onLoad(kind, buffer, stage)`` shows the file.
 */
export function bridge(source, onLoad) {
    const send = (data) => window.parent.postMessage(Object.assign({ source }, data), "*");
    const fail = (err) => {
        const text = err && err.message ? err.message : String(err);
        console.warn("[" + source + "] cannot display the file:", text);
        send({ type: "error", message: text });
    };
    window.addEventListener("error", (e) => fail(e.error || e.message));
    window.addEventListener("unhandledrejection", (e) => fail(e.reason));
    window.addEventListener("message", async (ev) => {
        const data = ev.data;
        if (ev.source !== window.parent || !data || data.source !== source + "_parent" || data.type !== "load") {
            return;
        }
        try {
            const stats = await onLoad(data.kind, data.buffer);
            send({ type: "rendered", stats: stats || {} });
        } catch (e) {
            fail(e);
        }
    });
    send({ type: "ready" });
    return { send, fail };
}

const BG = { light: 0xf3f4f6, dark: 0x20232a };
const MAX_PIXEL_RATIO = 2;

/**
 * Throw a clear error when the browser has no WebGL. Probe first: three.js and dxf-viewer log a console error when they
 * cannot create a context, and a missing WebGL (old or remote browsers, disabled hardware acceleration) is a normal
 * case that gets a message in the dialog (with the Download button).
 */
export function requireWebGL() {
    const probe = document.createElement("canvas");
    if (!(probe.getContext("webgl2") || probe.getContext("webgl"))) {
        throw new Error("WebGL is not available in this browser, so this file cannot be drawn. You can download it instead.");
    }
}

/** A WebGL stage: scene, camera, orbit controls, lights, toolbar (reset, wireframe, grid, axes, background). */
export function createStage(root) {
    const canvas = document.createElement("canvas");
    let renderer;
    requireWebGL();
    try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    } catch (e) {
        throw new Error("WebGL is not available in this browser, so this file cannot be drawn. You can download it instead.");
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
    root.appendChild(canvas);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(BG.light);
    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f98, 1.1));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    scene.add(key, key.target);
    const content = new THREE.Group();
    scene.add(content);
    const grid = new THREE.GridHelper(1, 20, 0x8a8f98, 0xc8cbd0);
    const axes = new THREE.AxesHelper(1);
    grid.visible = axes.visible = false;
    scene.add(grid, axes);
    const stage = { THREE, scene, camera, controls, renderer, content, root, home: null, wire: false };

    // "change" of the controls (fired by controls.update()) renders; render itself never calls update(): no loop
    const draw = () => {
        key.position.copy(camera.position).add(new THREE.Vector3(1, 2, 1));
        key.target.position.copy(controls.target);
        renderer.render(scene, camera);
    };
    controls.addEventListener("change", draw);
    const resize = () => {
        const w = Math.max(root.clientWidth, 1), h = Math.max(root.clientHeight, 1);
        renderer.setSize(w, h, false);
        canvas.style.width = "100%";
        canvas.style.height = "100%";
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        draw();
    };
    new ResizeObserver(resize).observe(root);
    // damping needs a loop only while the view is moving
    let moving = false;
    controls.addEventListener("start", () => {
        moving = true;
        const tick = () => {
            if (moving) {
                controls.update();
                requestAnimationFrame(tick);
            }
        };
        tick();
    });
    controls.addEventListener("end", () => setTimeout(() => (moving = false), 600));

    /** Put the camera where the whole content is visible (the model, or the drawing), looking from a corner. */
    stage.fit = (flat = false) => {
        // a viewer can give the box that matters (stage.fitBox): a stray far object must not shrink the model
        const box = stage.fitBox ? stage.fitBox.clone() : new THREE.Box3().setFromObject(content);
        if (box.isEmpty()) {
            return;
        }
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        const radius = Math.max(size.length() / 2, 1e-6);
        const dist = radius / Math.sin((camera.fov * Math.PI) / 360);
        camera.near = dist / 1000;
        camera.far = dist * 1000;
        camera.updateProjectionMatrix();
        const dir = flat ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0.8, 1).normalize();
        camera.position.copy(center).addScaledVector(dir, dist);
        controls.target.copy(center);
        controls.update();
        draw();
        grid.scale.setScalar(Math.max(size.x, size.z, radius) * 2);
        grid.position.set(center.x, box.min.y, center.z);
        axes.scale.setScalar(radius);
        axes.position.copy(box.min);
        stage.home = { position: camera.position.clone(), target: center.clone() };
        draw();
    };
    stage.setWireframe = (on) => {
        stage.wire = on;
        content.traverse((o) => {
            for (const m of [].concat(o.material || [])) {
                m.wireframe = on;
            }
        });
        draw();
    };
    stage.stats = () => {
        let triangles = 0, vertices = 0, objects = 0;
        content.traverse((o) => {
            if (o.geometry) {
                objects++;
                const pos = o.geometry.attributes.position;
                vertices += pos ? pos.count : 0;
                triangles += o.geometry.index ? o.geometry.index.count / 3 : pos ? pos.count / 3 : 0;
            }
        });
        const size = new THREE.Box3().setFromObject(content).getSize(new THREE.Vector3());
        return { triangles: Math.round(triangles), vertices, objects, size: [size.x, size.y, size.z] };
    };

    // toolbar
    const bar = document.createElement("div");
    bar.id = "bar";
    const button = (id, label, title, handler) => {
        const b = document.createElement("button");
        b.type = "button";
        b.id = id;
        b.textContent = label;
        b.title = title;
        b.addEventListener("click", () => handler(b));
        bar.appendChild(b);
        return b;
    };
    button("reset", "Reset view", "Fit the whole model in the view", () => stage.fit(stage.flat));
    const toggle = (id, label, title, apply) => {
        button(id, label, title, (b) => {
            const on = b.classList.toggle("on");
            b.setAttribute("aria-pressed", on);
            apply(on);
        });
    };
    stage.wireButton = () => {
        toggle("wire", "Wireframe", "Show the edges of the mesh", (on) => stage.setWireframe(on));
        bar.insertBefore(document.getElementById("wire"), document.getElementById("grid"));
    };
    toggle("grid", "Grid", "Show a grid under the model", (on) => ((grid.visible = on), draw()));
    toggle("axes", "Axes", "Show the X, Y and Z axes", (on) => ((axes.visible = on), draw()));
    toggle("dark", "Dark", "Dark background", (on) => ((scene.background = new THREE.Color(on ? BG.dark : BG.light)), draw()));
    const info = document.createElement("span");
    info.id = "info";
    bar.appendChild(info);
    root.parentElement.insertBefore(bar, root);
    stage.setInfo = (text) => (info.textContent = text);
    resize();
    return stage;
}

export function formatStats(s) {
    const n = (v) => v.toLocaleString("en-US");
    const dim = s.size.map((v) => (v >= 100 ? Math.round(v) : Math.round(v * 100) / 100)).join(" x ");
    return `${n(s.triangles)} triangles, ${n(s.vertices)} vertices, ${dim}`;
}
