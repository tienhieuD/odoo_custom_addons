import { A as e, F as t, v as n, y as r } from "./segment-line-BR56kM-V.js";
import { l as i, m as a, o, p as s, s as c, t as l } from "./paint-s8gGHFU5.js";
import { n as u, r as d } from "./drawingml-geometry-CIvPRuDI.js";
var f = 1;
function p(e, t, n) {
	let { x: r, y: i, w: a, h: o } = t.rect, { rotationDeg: s, flipH: c, flipV: l } = t.transform;
	e.save();
	try {
		(s !== 0 || c || l) && (e.translate(r + a / 2, i + o / 2), s !== 0 && e.rotate(s * Math.PI / 180), e.scale(c ? -1 : 1, l ? -1 : 1), e.translate(-(r + a / 2), -(i + o / 2))), n();
	} finally {
		e.restore();
	}
}
function m(e, n, r, i, a, o) {
	let s = n.resolvedGeometry ? u(n, n.resolvedGeometry.scale) : d(n, 1);
	if (a !== s.width || o !== s.height) throw RangeError("Retained DrawingML silhouette frame mismatch");
	t(e, s.fillSilhouette, r - s.originX, i - s.originY);
}
function h(e, t) {
	let { x: n, y: r, w: i, h: a } = t.rect;
	e.beginPath(), m(e, t, n, r, i, a), e.clip();
}
function g(e, t, n, r, i) {
	if (e.strokeStyle = o(t.color), l(e, n), t.fill) {
		let n = c(t.fill, e, r.x, r.y, r.w, r.h, i, f, void 0, void 0, s(e));
		n && (e.strokeStyle = n);
	}
}
function _(o, s, l) {
	let h = s.resolvedGeometry ? u(s, l) : d(s, l), _ = s.resolvedGeometry ? s : {
		...s,
		resolvedGeometry: h
	};
	i(s.stroke?.fill) && (o = a(o));
	let { x: v, y, w: b, h: x } = s.rect;
	p(o, s, () => {
		let i = c(s.fill, o, v, y, b, x, s.transform.rotationDeg, f, void 0, (e, t, n, r, i) => m(e, _, t, n, r, i)), a = s.stroke;
		for (let n of h.paths) {
			if (o.beginPath(), t(o, n.path, v - h.originX, y - h.originY), i && n.fill !== "none") {
				o.save();
				try {
					o.fillStyle = i, n.fillRule === "evenodd" ? o.fill("evenodd") : o.fill();
					let t = e(n.fill);
					t && (o.fillStyle = t, n.fillRule === "evenodd" ? o.fill("evenodd") : o.fill());
				} finally {
					o.restore();
				}
			}
			a && n.stroke && (g(o, a, n.stroke, s.rect, s.transform.rotationDeg), o.stroke());
		}
		if (a) for (let e of h.arrows) {
			let t = v - h.originX + e.tipX, i = y - h.originY + e.tipY;
			n(o, t, i, e.angle, e.geometry, a, r(o, a, l, f, t, i, e.angle, e.end, s.rect, s.transform.rotationDeg, f));
		}
	});
}
export { _ as n, p as r, h as t };
