import { C as e, D as t, E as n, I as r, L as i, P as a, R as o, S as s, T as c, j as l, m as u, p as d, w as f, z as p } from "./segment-line-BR56kM-V.js";
import { g as m, y as h } from "./paint-s8gGHFU5.js";
function g(e) {
	return JSON.stringify({
		geometry: e.geometry,
		stroke: e.stroke,
		fill: e.fill
	});
}
var _ = 1;
function v(r, m, v = Infinity) {
	let y = 0;
	if (!(v === Infinity || Number.isSafeInteger(v) && v > 0)) throw new a("Invalid DrawingML geometry budget");
	let b = (e) => {
		if (y += e, !Number.isSafeInteger(y) || y > v) throw new a("DrawingML geometry work budget exceeded");
	}, { x, y: S, w: C, h: w } = r.rect;
	if (![
		m,
		r.rect.x,
		r.rect.y,
		C,
		w,
		r.transform.rotationDeg
	].every(Number.isFinite) || m < 0 || C < 0 || w < 0) throw RangeError("Invalid DrawingML geometry frame");
	b(1);
	let T = r.stroke;
	if (b(T?.customDash?.length ?? 0), r.geometry.kind === "preset" && r.geometry.adjustments.some((e) => e !== null && !Number.isFinite(e))) throw RangeError("Non-finite DrawingML adjustment");
	let E = T ? h(T, m) : null, D = [], O = [], k = (e, t, n, r = "nonzero") => {
		D.push(Object.freeze({
			path: e,
			fill: t,
			stroke: n,
			fillRule: r
		}));
	}, A = (t, n, r, i) => {
		if (!i || !T) return;
		let a = e(i, T, m, _, b);
		if (a) {
			if (![
				t,
				n,
				r
			].every(Number.isFinite)) throw RangeError("Invalid resolved DrawingML arrow frame");
			O.push(Object.freeze({
				tipX: t,
				tipY: n,
				angle: r,
				end: Object.freeze({ ...i }),
				geometry: a
			}));
		}
	}, j = T?.headEnd ? s(T.headEnd, T, m, _) : 0, M = T?.tailEnd ? s(T.tailEnd, T, m, _) : 0, N = (e, t, n, r, i) => {
		if (!(r > 0 || i > 0) || !E) {
			k(e, t, E, n);
			return;
		}
		let a = f(e, r, i);
		b(a.reduce((e, t) => e + 1 + t.args.length, 0)), t !== "none" && k(e, t, null, n), k(a, "none", E, n);
	}, P = i(b);
	if (r.geometry.kind === "preset") {
		b(r.geometry.adjustments.length);
		let e = r.geometry.name.toLowerCase(), a = [...r.geometry.adjustments], o = u(e) && !!(T?.headEnd || T?.tailEnd), s = e.startsWith("curvedconnector"), p = l(e, C, w, a, b, x, S);
		if (p) p.forEach((e, t) => {
			let n = t === p.length - 1 && (e.fill === "none" || e.fill == null);
			s && n && e.stroke ? N(e.path, e.fill, "nonzero", j, M) : k(e.path, e.fill, e.stroke && !(o && n) ? E : null);
		});
		else {
			let t = i(b);
			c(t.sink, e, x, S, C, w, a[0], a[1], a[2], a[3]), k(Object.freeze(t.commands), null, E, "nonzero");
		}
		if (n(P.sink, r.geometry.name, x, S, C, w, a) || c(P.sink, r.geometry.name, x, S, C, w, a[0], a[1], a[2], a[3]), T && d(e)) {
			let n = t(e, x, S, C, w, a);
			if (n) {
				if (o && n.vertices.length >= 2) {
					let e = i(b), t = n.vertices;
					e.sink.moveTo(t[0].x, t[0].y);
					for (let n = 1; n < t.length; n++) e.sink.lineTo(t[n].x, t[n].y);
					let r = f(Object.freeze(e.commands), j, M);
					r.length >= 2 && k(r, "none", E);
				}
				A(n.end.x, n.end.y, n.end.angle, T.tailEnd), A(n.start.x, n.start.y, n.start.angle, T.headEnd);
			}
		}
	} else {
		let { subpaths: e } = r.geometry;
		for (let t of e) b(t.length + 1);
		let t = r.geometry.paint?.length === e.length ? r.geometry.paint : null, n = T && (j > 0 || M > 0) ? o(e) : null, a = n?.start ? j : 0, s = n?.end ? M : 0;
		if (t) e.forEach((n, r) => {
			let o = i(b);
			p(o.sink, [n], x, S, C, w);
			let c = Object.freeze(o.commands), l = t[r].fill ?? null;
			t[r].stroke === !1 ? k(c, l, null, t[r].fillRule) : N(c, l, t[r].fillRule ?? "nonzero", r === 0 ? a : 0, r === e.length - 1 ? s : 0);
		});
		else {
			let t = i(b);
			p(t.sink, e, x, S, C, w), N(Object.freeze(t.commands), null, "nonzero", a, s);
		}
		if (p(P.sink, t ? e.filter((e, n) => t[n].fill !== "none") : e, x, S, C, w), T) {
			let t = o(e);
			t.start && A(x + t.start.x * C, S + t.start.y * w, Math.atan2(t.start.dy * w, t.start.dx * C), T.headEnd), t.end && A(x + t.end.x * C, S + t.end.y * w, Math.atan2(t.end.dy * w, t.end.dx * C), T.tailEnd);
		}
	}
	return Object.freeze({
		width: C,
		height: w,
		scale: m,
		originX: x,
		originY: S,
		sourceKey: g(r),
		paths: Object.freeze(D),
		arrows: Object.freeze(O),
		fillSilhouette: Object.freeze(P.commands),
		workUnits: y
	});
}
function y(e, t) {
	let n = e.resolvedGeometry;
	if (![
		t,
		e.rect.x,
		e.rect.y,
		e.rect.w,
		e.rect.h,
		e.transform.rotationDeg
	].every(Number.isFinite) || t < 0 || e.rect.w < 0 || e.rect.h < 0 || typeof e.transform.flipH != "boolean" || typeof e.transform.flipV != "boolean") throw RangeError("Invalid retained DrawingML frame");
	if (!n || n.width !== e.rect.w || n.height !== e.rect.h || n.scale !== t || n.sourceKey !== g(e)) throw RangeError("Missing or stale retained DrawingML geometry");
	if (![n.originX, n.originY].every(Number.isFinite)) throw RangeError("Invalid retained DrawingML origin");
	if (!Number.isSafeInteger(n.workUnits) || n.workUnits < 1 || !Array.isArray(n.paths) || !Array.isArray(n.arrows)) throw RangeError("Invalid retained DrawingML work/scheduling");
	if (n.paths.length + n.arrows.length > n.workUnits) throw new a("Retained geometry scheduling exceeds its acquired work");
	let i = 0, o = (e) => {
		if (i += e, i > n.workUnits) throw new a("Retained geometry paths exceed their acquired work");
	}, s = (e) => {
		if (!Number.isFinite(e.lineWidth) || e.lineWidth < 0 || !Number.isFinite(e.miterLimit) || e.miterLimit <= 0 || ![
			"butt",
			"round",
			"square"
		].includes(e.lineCap) || ![
			"round",
			"bevel",
			"miter"
		].includes(e.lineJoin) || !Array.isArray(e.dash) || e.dash.length > n.workUnits || !e.dash.every((e) => Number.isFinite(e) && e >= 0)) throw RangeError("Invalid retained stroke geometry");
	};
	for (let e of n.paths) {
		if (r(e.path, o), e.fill !== null && ![
			"norm",
			"none",
			"lighten",
			"lightenLess",
			"darken",
			"darkenLess"
		].includes(e.fill)) throw RangeError("Invalid retained path fill");
		if (e.fillRule !== "nonzero" && e.fillRule !== "evenodd") throw RangeError("Invalid retained fill rule");
		e.stroke && s(e.stroke);
	}
	r(n.fillSilhouette, o);
	for (let e of n.arrows) {
		if (![
			e.tipX,
			e.tipY,
			e.angle
		].every(Number.isFinite) || !["fill", "stroke"].includes(e.geometry.paint)) throw RangeError("Invalid retained arrow frame");
		r(e.geometry.path, o), s(e.geometry.stroke);
	}
	return n;
}
function b(e, t) {
	let n = {
		a: e.a * t.a + e.c * t.b,
		b: e.b * t.a + e.d * t.b,
		c: e.a * t.c + e.c * t.d,
		d: e.b * t.c + e.d * t.d,
		e: e.a * t.e + e.c * t.f + e.e,
		f: e.b * t.e + e.d * t.f + e.f
	};
	if (!Object.values(n).every(Number.isFinite) || !Number.isFinite(n.a * n.d - n.b * n.c) || n.a * n.d - n.b * n.c === 0) throw RangeError("Invalid DrawingML geometry transform");
	return n;
}
var x = {
	a: 1,
	b: 0,
	c: 0,
	d: 1,
	e: 0,
	f: 0
}, S = (e, t) => ({
	...x,
	e,
	f: t
}), C = (e) => ({
	a: Math.cos(e),
	b: Math.sin(e),
	c: -Math.sin(e),
	d: Math.cos(e),
	e: 0,
	f: 0
});
function w(e, t = x) {
	let n = y(e, 1), { x: r, y: i, w: a, h: o } = e.rect, s = e.transform, c = t;
	(s.rotationDeg !== 0 || s.flipH || s.flipV) && (c = b(c, S(r + a / 2, i + o / 2)), s.rotationDeg !== 0 && (c = b(c, C(s.rotationDeg * Math.PI / 180))), c = b(c, {
		...x,
		a: s.flipH ? -1 : 1,
		d: s.flipV ? -1 : 1
	}), c = b(c, S(-(r + a / 2), -(i + o / 2)))), c = b(c, S(r - n.originX, i - n.originY));
	let l = [], u = h(null, 1), d = (e, t, n) => {
		let r = m(e, t, n);
		r && l.push(r);
	};
	for (let t of n.paths) e.fill && e.fill.fillType !== "none" && t.fill !== "none" && d(t.path, c, u), t.stroke && d(t.path, c, t.stroke);
	for (let e of n.arrows) {
		let t = b(b(c, S(e.tipX, e.tipY)), C(e.angle));
		d(e.geometry.path, t, e.geometry.paint === "stroke" ? e.geometry.stroke : u);
	}
	if (l.length === 0) return null;
	let f = Infinity, p = Infinity, g = -Infinity, _ = -Infinity;
	for (let e of l) f = Math.min(f, e.x), p = Math.min(p, e.y), g = Math.max(g, e.x + e.w), _ = Math.max(_, e.y + e.h);
	let v = {
		x: f,
		y: p,
		w: g - f,
		h: _ - p
	};
	if (!Object.values(v).every(Number.isFinite)) throw RangeError("Non-finite DrawingML enclosure");
	return v;
}
export { y as n, v as r, w as t };
