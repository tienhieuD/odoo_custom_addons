import { t as e } from "./worksheet-policy-G1KBtmuQ.js";
var t = /* @__PURE__ */ new WeakMap();
function n(e, n) {
	t.set(e, n);
}
function r(n) {
	return t.get(n) ?? e;
}
function i(e, n) {
	let r = t.get(e);
	r === void 0 ? t.delete(n) : t.set(n, r);
}
export { r as n, i as r, n as t };
