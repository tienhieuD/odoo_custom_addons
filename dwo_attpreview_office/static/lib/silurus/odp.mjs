import { n as e, r as t, t as n } from "./odf-source-Cee46vyi.js";
//#region src/wasm-odp/opendocument_odp_bg.wasm?url
var r = new URL("opendocument_odp_bg.wasm", import.meta.url).href, i = new URL("odp-source-module.mjs", import.meta.url).href;
//#endregion
//#region src/odp.ts
function a(e = {}) {
	if (typeof e != "object" || !e || Array.isArray(e)) throw TypeError("OpenDocument ODP source options must be an object");
	return n("odp", e, {
		wasmUrl: t(r, import.meta.url),
		moduleUrl: t(i, import.meta.url)
	});
}
var o = /* @__PURE__ */ e("pptx", () => a());
//#endregion
export { a as createOdp, o as odp };
