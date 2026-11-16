import { n as e, r as t, t as n } from "./odf-source-CcsC38G5.js";
//#region src/wasm-odt/opendocument_odt_bg.wasm?url
var r = new URL("opendocument_odt_bg.wasm", import.meta.url).href, i = new URL("odt-source-module.mjs", import.meta.url).href;
//#endregion
//#region src/odt.ts
function a(e = {}) {
	if (typeof e != "object" || !e || Array.isArray(e)) throw TypeError("OpenDocument ODT source options must be an object");
	return n("odt", e, {
		wasmUrl: t(r, import.meta.url),
		moduleUrl: t(i, import.meta.url)
	});
}
var o = /* @__PURE__ */ e("docx", () => a());
//#endregion
export { a as createOdt, o as odt };
