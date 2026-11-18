import { n as e, r as t, t as n } from "./odf-source-Cee46vyi.js";
//#region src/wasm-ods/opendocument_ods_bg.wasm?url
var r = new URL("opendocument_ods_bg.wasm", import.meta.url).href, i = new URL("ods-source-module.mjs", import.meta.url).href;
//#endregion
//#region src/ods.ts
function a(e = {}) {
	if (typeof e != "object" || !e || Array.isArray(e)) throw TypeError("OpenDocument ODS source options must be an object");
	return n("ods", e, {
		wasmUrl: t(r, import.meta.url),
		moduleUrl: t(i, import.meta.url)
	});
}
var o = /* @__PURE__ */ e("xlsx", () => a());
//#endregion
export { a as createOds, o as ods };
