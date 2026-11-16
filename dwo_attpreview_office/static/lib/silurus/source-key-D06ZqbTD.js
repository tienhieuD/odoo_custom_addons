function e(t, n = "$") {
	if (t === null || typeof t == "boolean" || typeof t == "number" || typeof t == "string") return JSON.stringify(t);
	if (Array.isArray(t)) return `[${t.map((t, r) => e(t, `${n}[${r}]`)).join(",")}]`;
	if (typeof t == "object") {
		let r = t;
		return `{${Object.keys(r).sort().map((t) => `${JSON.stringify(t)}:${e(r[t], `${n}.${t}`)}`).join(",")}}`;
	}
	throw TypeError(`Cannot fingerprint ${typeof t} at ${n}`);
}
function t(t, n) {
	let r = e(n);
	return `${t}:${encodeURIComponent(r)}`;
}
function n(e) {
	return `${e.story}:${encodeURIComponent(e.storyInstance)}:${e.path.join(".")}`;
}
function r(e, t, r) {
	if (t.length === 0 || r.length === 0) throw RangeError("Body occurrence identity requires a flow domain and fragment start");
	return [
		"body-occurrence",
		encodeURIComponent(n(e)),
		encodeURIComponent(t),
		encodeURIComponent(r)
	].join("/");
}
function i(e) {
	return [
		e.rowIndex,
		e.rowFragmentIndex,
		e.cells.map((e) => [
			e.blockIndex,
			e.paragraphLineStart,
			e.nestedFragmentIndex,
			e.nestedCursor === null ? null : i(e.nestedCursor)
		])
	];
}
function a(e) {
	if (e === void 0) return "root";
	if (e.kind === "table") return `table:${JSON.stringify(i(e.cursor))}`;
	let t = e.cursor.tableCursor;
	return `adjacent-table:${e.cursor.tableIndex}:${e.cursor.sourceRowIndex}:${JSON.stringify(t === void 0 ? null : i(t))}`;
}
function o(e, t, n, r) {
	return `table:${e.path.join(".")}:root:${t}:${n}:${r}`;
}
function s(e, t) {
	return `image:${n(e)}:${encodeURIComponent(t)}`;
}
function c(e, t) {
	return `vml-picture:${n(e)}:${encodeURIComponent(t)}`;
}
function l(e, t) {
	return `math:${n(e)}:${encodeURIComponent(t)}`;
}
function u(e) {
	return t("chart-resource", e);
}
function d(e, t) {
	return `anchor:${n(e)}:${encodeURIComponent(t)}`;
}
function f(e, t) {
	return `${s(e, t)}:vml-stroke`;
}
function p(e, t = "") {
	return `vml-edge:${n(e)}:${t}`;
}
export { s as a, a as c, f as d, t as f, u as i, p as l, r as n, l as o, o as r, n as s, d as t, c as u };
