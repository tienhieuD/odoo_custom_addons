import { t as e } from "./model-source-BwpDCGYU.js";
var t = "0.90.1", n = class extends Error {
	constructor(n, r) {
		super(`Companion requires @silurus/ooxml ${n} (${r}); installed runtime is ${t} (${e})`), this.code = "companion-runtime-mismatch", this.name = "CompanionRuntimeMismatchError";
	}
};
function r(e, t) {
	if (e !== "0.90.1" || t !== "ooxml-model-source-module/v2") throw new n(e, t);
}
export { n as CompanionRuntimeMismatchError, e as MODEL_SOURCE_MODULE_PROTOCOL, r as assertCompanionRuntime };
