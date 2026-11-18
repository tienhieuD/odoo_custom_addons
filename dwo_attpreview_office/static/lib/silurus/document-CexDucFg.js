import { n as e } from "./own-key-CzMRhMxt.js";
import { n as t } from "./ooxml-error-DbICW35n.js";
import { n, t as r } from "./cfb-guard-reswPjey.js";
import { n as i } from "./font-registry-CA7E7o7P.js";
import { m as a } from "./resource-policy.generated-D_HlV2Rm.js";
import { i as o, n as s, r as c, t as l } from "./embedded-B4q5SDVm.js";
import { d as u } from "./scripts-DxEAUeVI.js";
import { i as d, n as f } from "./office-fallback-O-L6rrDh.js";
import { B as p, Ci as m, H as h, Xt as g, _t as _, bi as v, di as y, dt as b, fi as x, gi as S, gt as C, hi as w, tt as T, ui as E, vi as D, yi as O } from "./document-content-DXDaB_ij.js";
import { t as ee } from "./open-type-metrics-BlHDsmjh.js";
import { n as k } from "./cjk-fallback-CxqXJu32.js";
import { u as A } from "./vertical-vert-feature-ru96Mg5B.js";
import { f as te } from "./pixel-budget-DI82Hn3R.js";
import { i as ne, l as re, m as ie, o as ae, s as oe } from "./duotone-bitmap-by-path-B_pNKO0M.js";
import { n as se } from "./renderer-module-contract-BuTx2FWJ.js";
import { c as ce, i as le, n as ue, r as de, s as fe, t as pe } from "./chart-context-DqNY4BWJ.js";
import { n as me, r as he } from "./error-wire-Dr1HjXGZ.js";
import { i as ge, n as _e, r as ve } from "./resource-debug-D8EBjKbZ.js";
import { t as ye } from "./rejected-load-CS5sDp04.js";
import "./pull-session-CJuB3jmq.js";
import { t as be } from "./bundled-asset-url-Cv8ajMAZ.js";
import { u as j } from "./source-GXgH3t1X.js";
import { n as xe } from "./chart-font-sources-B96UtO2E.js";
import { c as Se, l as Ce, o as we, r as Te, s as Ee, u as De } from "./part-failures-pZSloLZv.js";
import { t as Oe } from "./bounded-raw-part-cache-TU72wntZ.js";
import { n as ke, r as Ae, t as je } from "./deferred-D2gd0MY2.js";
import { E as Me, S as Ne, T as M, _ as Pe, a as Fe, b as Ie, c as Le, f as Re, g as N, h as ze, l as Be, m as Ve, n as P, o as He, p as Ue, s as We, t as F, u as Ge, v as Ke, w as qe, x as Je } from "./document-pull-client-DsaDuAP-.js";
import { s as I } from "./source-key-D06ZqbTD.js";
import { i as Ye, r as Xe, t as Ze } from "./comments-B3a2O0op.js";
function Qe(e, t) {
	if (e.metric.lineHeightRatio != null || !t) return e.metric;
	let n = u(e.requestedFamily, {
		weight: e.weight,
		style: e.style
	});
	if (e.source !== "substitute" && n.some((e) => e.farEastCodePage !== !1)) return e.metric;
	let r = t.ascentRatio + t.lineGapRatio, i = t.descentRatio;
	return Number.isFinite(r) && Number.isFinite(i) && r >= 0 && i >= 0 && r + i > 0 ? Object.freeze({
		...e.metric,
		requiresGlyphCoverage: !0,
		lineHeightRatio: r + i,
		designAscentRatio: r,
		designDescentRatio: i,
		lineGapRatio: t.lineGapRatio,
		normalAscentRatio: t.ascentRatio,
		normalDescentRatio: t.descentRatio,
		normalLineGapRatio: t.lineGapRatio,
		...n.length > 0 && e.source === "local" ? { farEastCodePage: !1 } : {}
	}) : e.metric;
}
function $e(e) {
	if (e.metric.lineHeightRatio != null) return;
	let t = u(e.requestedFamily, {
		weight: e.weight,
		style: e.style
	});
	return e.source === "substitute" || t.every((e) => e.farEastCodePage === !1) ? t[0]?.unitsPerEm : void 0;
}
async function et(e) {
	let t = typeof document > "u" ? null : document;
	return Promise.all(e.map(async (e) => {
		let n = $e(e), r = nt(e), i = t?.body && r && n ? await v(r, e.family, e.weight, e.style, n, t) : null;
		return {
			resourceIdentity: e.resourceIdentity,
			weight: e.weight,
			style: e.style,
			measured: i
		};
	}));
}
function tt(e) {
	if (e.source !== "local" || e.weight !== 400 || e.style !== "normal") return !1;
	let t = u(e.requestedFamily);
	return !t.some((e) => e.weight >= 600 && e.style === "normal") || !t.some((e) => e.style === "italic");
}
function nt(e) {
	return e.source === "local" && e.resourceIdentity.startsWith("office-local:local(") ? e.resourceIdentity.slice(13) : void 0;
}
async function rt(t, n, r) {
	let i = typeof document > "u" ? null : document;
	if (!n) return t;
	let a = i?.body && i.fonts === n ? i.createElement("canvas").getContext("2d") : null, o = /* @__PURE__ */ new Map(), s = await Promise.all(Object.entries(t.routes).map(async ([e, s]) => {
		let c = t.faces.find((e) => e.family === s.family), l = $e(s), u = r?.find((e) => e.resourceIdentity === s.resourceIdentity && e.weight === s.weight && e.style === s.style), d = Qe(s, c && l && a && i?.body ? O(c, n, a, l, i) : u?.measured ?? null), f = nt(s), p = null, m;
		if (c && f && tt(s)) {
			let e = o.get(c);
			e || (e = D(c, f, n), o.set(c, e)), m = (await e)?.family;
		}
		if (d !== s.metric) {
			if (c && f) {
				let e = o.get(c);
				e || (e = D(c, f, n), o.set(c, e)), p = await e;
			}
			d = p ? Object.freeze({
				...d,
				glyphCoverageProbeFamily: p.family
			}) : s.metric;
		}
		return {
			key: e,
			route: {
				...s,
				metric: d,
				...m ? { coverageProbeFamily: m } : {}
			},
			probe: p
		};
	})), c = e();
	for (let e of s) c[e.key] = e.route;
	for (let e of o.values()) {
		let n = await e;
		n && t.faces.push(n);
	}
	return {
		...t,
		routes: c
	};
}
async function it(...e) {
	return rt(await f(...e), e[1] === void 0 ? i() : e[1]);
}
var L = /* @__PURE__ */ new WeakMap();
function R(e, t = []) {
	let n = L.get(e) ?? [], r = new Map(n.map((e) => [JSON.stringify(e), e]));
	for (let e of t) r.set(JSON.stringify(e), Object.freeze({ ...e }));
	L.set(e, Object.freeze([...r.values()]));
}
function at(e) {
	return L.get(e) ?? [];
}
var ot = "var e=(e,t)=>()=>(e&&(t=e(e=0)),t);function t(e){if(!e.startsWith(`data:`))return null;let t=e.indexOf(`,`);if(t===-1)return null;let n=atob(e.slice(t+1)),r=new Uint8Array(n.length);for(let e=0;e<n.length;e++)r[e]=n.charCodeAt(e);return r.buffer}var n,r,i=e((()=>{n=class e extends Error{code;details;violation;constructor(t,n,r){super(n),this.name=`OoxmlError`,this.code=t,t===`unsupported-content`&&r&&`format`in r&&(this.details=Object.freeze({format:r.format,reason:r.reason})),t===`font-source-limit`&&r&&`quota`in r&&(this.violation=Object.freeze({resource:`font-source`,quota:r.quota,metric:r.metric,limit:r.limit,observed:r.observed})),Object.setPrototypeOf(this,e.prototype)}},r=class e extends Error{code=`ooxml-resource-limit`;details;constructor(t,n){super(t),this.name=`OoxmlResourceLimitError`;let r=n.violation,i=Object.freeze({format:r.format,operation:r.operation,resource:r.resource,metric:r.metric,...r.part===void 0?{}:{part:r.part},limit:r.limit,observed:r.observed,configurable:r.configurable,usage:Object.freeze({archiveEntryCount:r.usage.archiveEntryCount,declaredInflatedBytes:r.usage.declaredInflatedBytes,...r.usage.largestInflatedEntryBytes===void 0?{}:{largestInflatedEntryBytes:r.usage.largestInflatedEntryBytes},distinctInflatedBytes:r.usage.distinctInflatedBytes,operationInflatedBytes:r.usage.operationInflatedBytes})});this.details=Object.freeze({stage:n.stage,violation:i}),Object.setPrototypeOf(this,e.prototype)}}}));const a={stylesheet:`bytes`,declarations:`entry-count`,families:`entry-count`,face:`bytes`,retained:`bytes`,url:`length`};function o(e){return typeof e==`number`&&Number.isSafeInteger(e)&&e>=0}function s(e){return`Font source limit exceeded (${e.quota}): ${e.metric} ${e.observed} > ${e.limit}`}function c(e){if(!e||typeof e!=`object`||Array.isArray(e))return;let{resource:t,quota:n,metric:r,limit:i,observed:s}=e;if(t!==`font-source`||typeof n!=`string`||!Object.prototype.hasOwnProperty.call(a,n))return;let c=n;if(!(r!==a[c]||!o(i)||!o(s)||s<=i))return{resource:t,quota:c,metric:a[c],limit:i,observed:s}}function l(e){return e===`image-dimension`||e===`image-pixels`||e===`active-decoded-bytes`||e===`image-effect-count`||e===`image-effect-work`||e===`tiff-lzw-work`||e===`metafile-path-commands`||e===`metafile-record-points`||e===`metafile-record-polygons`||e===`metafile-record-rectangles`||e===`metafile-record-text-units`}function u(e){return typeof e==`number`&&Number.isSafeInteger(e)&&e>=0}function ee(e){if(!(!e||typeof e!=`object`))try{let t=e,n=t.code,r=t.metric,i=t.limit,a=t.observed;return n!==`ooxml-decoded-image-limit`||!l(r)||!u(i)||!u(a)||a<=i?void 0:{metric:r,limit:i,observed:a}}catch{return}}var d,f,p,m,h,te=e((()=>{d=1<<25,f=1<<27,d*4,f*4,p=Math.floor(d/4),m=f,m/p,h=class e extends RangeError{metric;limit;observed;code=`ooxml-decoded-image-limit`;constructor(t,n,r){super(`OOXML decoded image limit exceeded: ${t} ${r} > ${n}`),this.metric=t,this.limit=n,this.observed=r,this.name=`OoxmlDecodedImageLimitError`,Object.setPrototypeOf(this,e.prototype)}}}));function ne(e){if(!(typeof e!=`object`||!e))try{let t=e,n=t.code,r=t.message;return n===`ooxml-tiff-decode`&&typeof r==`string`?{message:r}:void 0}catch{return}}var re=e((()=>{}));function g(e){return typeof e==`number`&&Number.isSafeInteger(e)&&e>0}function ie(e){if(!e||typeof e!=`object`||Array.isArray(e))return!1;let t=e;return g(t.requiredBytes)&&g(t.offeredBytes)&&t.requiredBytes>t.offeredBytes}var _=class e extends RangeError{code=`ooxml-insufficient-credit`;requiredBytes;offeredBytes;constructor(t){super(`Pull unit requires ${t.requiredBytes} bytes but credit is ${t.offeredBytes}`),this.name=`PullSessionInsufficientCreditError`,this.requiredBytes=t.requiredBytes,this.offeredBytes=t.offeredBytes,Object.setPrototypeOf(this,e.prototype)}};function v(e){if(e instanceof _)return e;let t=e instanceof Error?e.message:String(e);if(!t.startsWith(`OOXML_INSUFFICIENT_CREDIT:`))return;let n;try{n=JSON.parse(t.slice(26))}catch{return}if(!n||typeof n!=`object`||Array.isArray(n))return;let r=n;if(!(r.code!==`ooxml-insufficient-credit`||!ie(r)))return new _(r)}function ae(e,t,n){let r=v(e);if(!(!r||r.offeredBytes!==t||r.requiredBytes>n))return r}i(),te(),re();const y=`OOXML_RESOURCE_LIMIT:`;function b(e){return typeof e==`number`&&Number.isSafeInteger(e)&&e>=0}function oe(e){if(!e||typeof e!=`object`||Array.isArray(e))return!1;let t=e;return b(t.archiveEntryCount)&&b(t.declaredInflatedBytes)&&(t.largestInflatedEntryBytes===void 0||b(t.largestInflatedEntryBytes))&&b(t.distinctInflatedBytes)&&b(t.operationInflatedBytes)}function se(e){let t;try{t=JSON.parse(new TextDecoder().decode(e))}catch{throw TypeError(`OOXML resource usage checkpoint is not valid JSON`)}if(!oe(t))throw TypeError(`OOXML resource usage checkpoint is invalid`);return t}function ce(e){return e===`docx`||e===`xlsx`||e===`pptx`}function le(e){return e===`container`||e===`decompression`||e===`parsing`||e===`serialization`||e===`layout`||e===`rendering`||e===`worker`}function x(e,t){return typeof e==`string`&&e.length>0&&e.length<=t&&!/[\\u0000-\\u001f\\u007f]/u.test(e)}function S(e){return x(e,128)&&/^[a-z0-9][a-z0-9-]*$/u.test(e)}function ue(e){return!x(e,4096)||e.startsWith(`/`)||e.startsWith(`\\\\`)||e.includes(`\\\\`)||e.includes(`?`)||e.includes(`#`)||e.includes(`://`)||/^[a-z]:/iu.test(e)?!1:e.split(`/`).every(e=>e!==``&&e!==`.`&&e!==`..`)}const C=new Map([[`archive-entry:declared-inflated-bytes`,{stage:`container`,part:`required`}],[`archive-entry:actual-inflated-bytes`,{stage:`decompression`,part:`required`}],[`archive:entry-count`,{stage:`container`,part:`forbidden`}],[`archive:central-directory-bytes`,{stage:`container`,part:`forbidden`,configurable:!1}],[`archive:distinct-inflated-bytes`,{stage:`decompression`,part:`required`}],[`xml-event:bytes`,{stage:`parsing`,part:`optional`,configurable:!1}],[`xml-context:bytes`,{stage:`parsing`,part:`optional`,configurable:!1}],[`image-effect:work`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`chartex-allocation:elements`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`chartex-allocation:bytes`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`chart-cache:points`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`numbering-marker:bytes`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`chart-style-formats:entries`,{stage:`parsing`,part:`required`,configurable:!1}],[`chart-custom-number-formats:entries`,{stage:`parsing`,part:`required`,configurable:!1}],[`chart-number-format-bytes:bytes`,{stage:`parsing`,part:`required`,configurable:!1}],[`xml-tree:depth`,{stage:`parsing`,part:`optional`,configurable:!1}],[`worksheet-row:projected-bytes`,{stage:`parsing`,part:`optional`,configurable:!1}],[`worksheet-shell:projected-bytes`,{stage:`parsing`,part:`optional`,configurable:!1}],[`theme-style-reparse:bytes`,{stage:`parsing`,part:`forbidden`,configurable:!1}],[`style-inheritance:depth`,{stage:`parsing`,part:`required`,configurable:!1}],[`complex-field:depth`,{stage:`parsing`,part:`forbidden`,configurable:!1}]]),de=new Set([...C.keys()].map(e=>e.slice(0,e.indexOf(`:`)))),fe=new Set([...C.keys()].map(e=>e.slice(e.indexOf(`:`)+1)));function pe(e){if(!e||typeof e!=`object`||Array.isArray(e))return!1;let t=e;return!ce(t.format)||!x(t.operation,256)||!S(t.resource)||!S(t.metric)||!b(t.limit)||!b(t.observed)||typeof t.configurable!=`boolean`||!oe(t.usage)?!1:!(`part`in t)||ue(t.part)}function w(e){if(!e||typeof e!=`object`||Array.isArray(e))return!1;let t=e;if(!le(t.stage)||!pe(t.violation))return!1;let n=t.violation,r=C.get(`${n.resource}:${n.metric}`);return r?t.stage!==r.stage||r.configurable===!1&&n.configurable!==!1?!1:r.part===`required`?n.part!==void 0:r.part===`forbidden`?n.part===void 0:!0:!(de.has(n.resource)&&fe.has(n.metric))}function me(e){return{archiveEntryCount:e.archiveEntryCount,declaredInflatedBytes:e.declaredInflatedBytes,...e.largestInflatedEntryBytes===void 0?{}:{largestInflatedEntryBytes:e.largestInflatedEntryBytes},distinctInflatedBytes:e.distinctInflatedBytes,operationInflatedBytes:e.operationInflatedBytes}}function he(e){if(!w(e))return;let t=e.violation,n={stage:e.stage,violation:{format:t.format,operation:t.operation,resource:t.resource,metric:t.metric,...t.part===void 0?{}:{part:t.part},limit:t.limit,observed:t.observed,configurable:t.configurable,usage:me(t.usage)}};return w(n)?n:void 0}function T(e){let t=e.violation;return`OOXML resource limit exceeded${t.part?` for ${t.part}`:``} (${t.resource}, ${e.stage}): ${t.metric} ${t.observed} > ${t.limit}`}function ge(e){let t=e instanceof Error?e.message:String(e);if(!t.startsWith(y))return;let n;try{n=JSON.parse(t.slice(21))}catch{return}if(!n||typeof n!=`object`)return;let i=n;if(!(i.code!==`ooxml-resource-limit`||!w(i.details)))return new r(T(i.details),i.details)}function _e(e){try{return e()}catch(e){throw e instanceof r||typeof e!=`string`&&!(e instanceof Error)?e:ge(e)??e}}function ve(e){let t=e instanceof Error?e.message:String(e);if(t.startsWith(`OOXML_NOT_OOXML:`))return new n(`not-ooxml`,`This file is not an Office Open XML document: ${t.slice(16)}`)}function E(e){if(!e||typeof e!=`object`||Array.isArray(e))return;let t=e,n=t.format,r=t.reason;if(!(!S(n)||r!==`source-subset`))return{format:n,reason:r}}function D(e){return new n(`unsupported-content`,`Input is outside the source’s supported subset.`,e)}function ye(e){let t=typeof e==`string`?e:e instanceof Error?e.message:``;if(!(!t.startsWith(`MODEL_SOURCE_UNSUPPORTED:`)||t.length>1024))try{let e=E(JSON.parse(t.slice(25)));return e?D(e):void 0}catch{return}}function be(e){return e===`OOXML_SOURCE_UNSUPPORTED_ENCRYPTION`||e instanceof Error&&e.message===`OOXML_SOURCE_UNSUPPORTED_ENCRYPTION`?new n(`unsupported-encryption`,`The configured source cannot decrypt this input.`):ye(e)??ge(e)??ve(e)}function xe(e){let t=ee(e);if(t){let e=new h(t.metric,t.limit,t.observed);return{message:e.message,errorName:e.name,code:e.code,decodedImage:t}}let i=ne(e);if(i)return{message:i.message,errorName:`TiffDecodeError`,code:`ooxml-tiff-decode`};let a=v(e);if(a)return{message:a.message,errorName:a.name,code:a.code,insufficientCredit:{requiredBytes:a.requiredBytes,offeredBytes:a.offeredBytes}};let o=e instanceof n||e instanceof r?e:be(e),l=o??e;if(o instanceof r||l&&typeof l==`object`&&l.code===`ooxml-resource-limit`){let e=l,t=he(e.details);return t?{message:typeof e.message==`string`?e.message:T(t),errorName:`OoxmlResourceLimitError`,code:`ooxml-resource-limit`,resourceLimit:t}:{message:`Invalid OOXML resource-limit error payload`,errorName:`Error`}}if(l&&typeof l==`object`&&l.code===`unsupported-content`){let e=E(l.details);return e?{message:D(e).message,code:`unsupported-content`,unsupportedContent:e}:{message:`Invalid unsupported-content error payload`,errorName:`Error`}}if(l&&typeof l==`object`&&l.code===`font-source-limit`){let e=c(l.violation);return e?{message:s(e),errorName:`OoxmlError`,code:`font-source-limit`,fontSourceLimit:e}:{message:`Invalid font-source-limit error payload`,errorName:`Error`}}if(o instanceof n)return{message:typeof o.message==`string`?o.message:String(o.message),errorName:x(o.name,128)?o.name:`OoxmlError`,...S(o.code)?{code:o.code}:{}};let u=e instanceof Error?e.message:String(e);if(typeof u==`string`&&u.startsWith(y))return{message:`Invalid OOXML resource-limit payload`,errorName:`Error`};let d=e instanceof Error?e:Error(u),f=d;return{message:typeof d.message==`string`?d.message:String(d.message),errorName:x(d.name,128)?d.name:`Error`,...typeof f.code==`string`?{code:f.code}:{}}}function O(e){try{return xe(e)}catch{return{message:`Worker operation failed with an unreadable error`,errorName:`Error`}}}var Se=class{initialize;reinitialize;normalizeFailure;state=`uninitialized`;generationValue=0;readiness;poisonListeners=new Set;constructor(e,t,n){this.initialize=e,this.reinitialize=t,this.normalizeFailure=n}get generation(){return this.generationValue}get poisoned(){return this.state===`poisoned`}onPoison(e){return this.poisonListeners.add(e),()=>this.poisonListeners.delete(e)}async ensureReady(){if(this.state!==`ready`){if(!this.readiness){let e=this.state===`uninitialized`?this.initialize:this.reinitialize;this.readiness=Promise.resolve().then(e).then(()=>{this.generationValue+=1,this.state=`ready`,this.readiness=void 0},e=>{throw this.readiness=void 0,e})}await this.readiness}}run(e){try{return e()}catch(e){let t=this.normalizeFailure(e);throw t?(this.poison(t),t):e}}tryRunReady(e){if(this.state!==`ready`)return{current:!1};let t=this.generationValue,n=this.run(e);return this.state!==`ready`||t!==this.generationValue?{current:!1}:{current:!0,generation:t,value:n}}poison(e){this.state=`poisoned`,this.readiness=void 0;for(let t of this.poisonListeners)t(e)}assertCurrent(e){if(this.state!==`ready`||e!==this.generationValue)throw Error(`WASM archive session belongs to a discarded runtime generation`)}},k=class e extends Error{code=`parser-crashed`;constructor(t){super(t),this.name=`WasmTrapError`,Object.setPrototypeOf(this,e.prototype)}};function Ce(e){let t=globalThis.WebAssembly?.RuntimeError;return t&&e instanceof t||e instanceof RangeError?!0:e instanceof Error?e.name===`RuntimeError`||e.name===`CompileError`||e.name===`LinkError`||e.name===`InternalError`||e.name===`OOMError`:!1}function we(e){try{if((typeof e!=`object`||!e)&&typeof e!=`function`)return;let t=Reflect.get(e,`__destroy_into_raw`);typeof t==`function`&&Reflect.apply(t,e,[])}catch{}}function Te(e,t){return e({module_or_path:t})}var Ee=class{init;options;runtime;wasmInput=null;currentArchive=null;constructor(e,t={}){this.init=e,this.options=t,this.runtime=new Se(()=>this.invokeConfigured(this.init),()=>this.invokeConfigured(this.options.reinit??this.init),De),this.runtime.onPoison(()=>this.dropPoisonedArchive())}setWasmInput(e){this.wasmInput=e,this.runtime.ensureReady().catch(()=>void 0)}setWasmUrl(e){this.setWasmInput(e)}get archive(){return this.currentArchive}setArchive(e){this.freeArchive(),this.currentArchive=e}disposeArchive(){this.freeArchive()}get poisoned(){return this.runtime.poisoned}async ensureReady(){await this.runtime.ensureReady()}run(e){return _e(()=>this.runtime.run(e))}poison(){this.runtime.poison(new k(`WASM parser was recycled`))}invokeConfigured(e){return this.wasmInput===null?Promise.reject(Error(`WasmParserHost: setWasmInput was never called`)):Te(e,this.wasmInput)}freeArchive(){this.currentArchive!==null&&this.options.freeArchive&&this.options.freeArchive(this.currentArchive),this.currentArchive=null}dropPoisonedArchive(){let e=this.currentArchive;this.currentArchive=null,we(e)}};function De(e){return Ce(e)?new k(`WASM parser trapped and was recycled: ${e instanceof Error?e.message:String(e)}`):null}function Oe(e){return e.byteOffset===0&&e.byteLength===e.buffer.byteLength&&e.buffer instanceof ArrayBuffer?e.buffer:e.slice().buffer}Object.freeze({maxArchiveEntryBytes:134217728,maxTotalInflatedBytes:268435456,maxArchiveEntries:4096});function ke(e){return[e.maxArchiveEntryBytes===null?0n:BigInt(e.maxArchiveEntryBytes),e.maxTotalInflatedBytes===null?0n:BigInt(e.maxTotalInflatedBytes),e.maxArchiveEntries===null?0n:BigInt(e.maxArchiveEntries)]}const A=`ooxml-pull-v1`;function j(e,t){if(!Number.isSafeInteger(e)||e<=0)throw RangeError(`${t} must be a positive safe integer`)}function Ae(e){if(!(typeof e==`string`&&e.length>0||typeof e==`number`&&Number.isSafeInteger(e)&&e>0))throw RangeError(`session id must be a non-empty string or positive safe integer`)}var M=class{owner;queue=Promise.resolve();leases=new Map;retainedBytes=0;retainedCount=0;maxRetainedBytes;maxRetainedCount;cleanups=new Set;pendingFatalCleanups=[];poisonRunning=!1;fatal;constructor(e){this.maxRetainedBytes=e?.maxRetainedBytes??64*1024*1024,this.maxRetainedCount=e?.maxRetainedCount??256,j(this.maxRetainedBytes,`max retained lease bytes`),j(this.maxRetainedCount,`max retained lease count`)}enqueue(e){let t=this.queue.then(e,e);return this.queue=t.then(()=>void 0,()=>void 0),t}acquire(e){return this.owner===void 0?(this.owner=e,!0):this.owner===e}release(e){this.owner===e&&(this.owner=void 0)}retainLease(e,t,n){if(!Number.isSafeInteger(n)||n<0)throw RangeError(`retained lease bytes are invalid`);let r=this.leases.get(e)??new Map;if(r.has(t))throw Error(`driver returned a duplicate lease id`);if(this.retainedCount+1>this.maxRetainedCount)throw RangeError(`retained lease count exceeds limit`);if(this.retainedBytes+n>this.maxRetainedBytes)throw RangeError(`retained lease bytes exceed limit`);r.set(t,n),this.leases.set(e,r),this.retainedCount++,this.retainedBytes+=n}releaseLease(e,t){let n=this.leases.get(e),r=n?.get(t);r!==void 0&&(n?.delete(t),n?.size===0&&this.leases.delete(e),this.retainedCount--,this.retainedBytes-=r)}registerCleanup(e){return this.fatal?(this.poisonRunning?this.pendingFatalCleanups.push(e):this.enqueue(e).catch(()=>void 0),()=>void 0):(this.cleanups.add(e),()=>this.cleanups.delete(e))}get fatalError(){return this.fatal}get registeredHostCount(){return this.cleanups.size}async poison(e){if(this.fatal??=e,this.poisonRunning)return this.fatal;this.poisonRunning=!0,this.pendingFatalCleanups.push(...this.cleanups);try{let e;for(;(e=this.pendingFatalCleanups.shift())!==void 0;)await e().catch(()=>void 0)}finally{this.poisonRunning=!1}return this.fatal}},je=class{options;coordinator;coordinatorOwner=Symbol(`pull-session-host`);unregisterCleanup;sequence=0;unacked;leases=new Map;activeDriverLeases=new Set;nextWireLeaseId;cancelRequested=!1;cancelComplete=!1;closeRequested=!1;closeComplete=!1;driverCancelComplete=!1;driverCloseComplete=!1;completed=!1;constructor(e){Ae(e.sessionId),j(e.operationId,`operation id`),j(e.generation,`generation`),j(e.maxByteCredit,`max byte credit`),e.wireLeaseIdStart!==void 0&&j(e.wireLeaseIdStart,`wire lease id start`),this.options=e,this.coordinator=e.coordinator,this.nextWireLeaseId=e.wireLeaseIdStart??1,this.unregisterCleanup=this.coordinator.registerCleanup(()=>this.forceFatalCleanup())}dispatch(e,t){return this.coordinator.enqueue(async()=>{let n=await this.execute(e);try{t(n.response,n.transfer)}catch(e){throw await this.rollbackFailedPost(n),e}})}async rollbackFailedPost(e){let t=e.response;if(t.kind===`chunk`){let n=t.leaseId===void 0?void 0:this.leases.get(t.leaseId);try{await this.options.driver.disposeInvalidChunk?.({payload:t.payload,byteLength:t.byteLength,done:t.done,leaseId:n?.driverLeaseId,retainedBytes:n?.retainedBytes,transfer:e.transfer})}catch{}}this.unacked=void 0,this.coordinator.release(this.coordinatorOwner);for(let[e,t]of[...this.leases])try{await this.options.driver.releaseLease?.(t.driverLeaseId)}catch{}finally{this.leases.delete(e),this.activeDriverLeases.delete(t.driverLeaseId),this.coordinator.releaseLease(this.coordinatorOwner,e)}if(this.cancelRequested=!0,!this.driverCancelComplete)try{await this.options.driver.cancel?.(),this.driverCancelComplete=!0}catch{}this.unregisterCleanup()}async execute(e){try{if(this.isStaleLifecycle(e)){let t=e.kind===`cancel`?`cancel`:`close`;return this.sameOperationIdentity(e)?{response:this.accepted(e,t,!0)}:{response:this.errorResponse(e,{message:`stale lifecycle targets another session or operation`,errorName:`PullSessionProtocolError`,code:`ooxml-stale-lifecycle`})}}this.validateCommandIdentity(e);let t=this.coordinator.fatalError;if(t)return e.kind===`pull`?{response:this.errorResponse(e,t)}:(e.kind===`cancel`?await this.cancel():e.kind===`close`?await this.close():e.kind===`release`&&await this.release(e.leaseId),{response:this.accepted(e,e.kind)});switch(e.kind){case`pull`:return await this.pull(e);case`ack`:return await this.ack(e.sequence),{response:this.accepted(e,`ack`)};case`release`:return await this.release(e.leaseId),{response:this.accepted(e,`release`)};case`cancel`:return await this.cancel(),{response:this.accepted(e,`cancel`)};case`close`:return await this.close(),{response:this.accepted(e,`close`)}}}catch(t){let n=O(t);return n.code===`ooxml-resource-limit`&&(n=await this.coordinator.poison(n)),{response:this.errorResponse(e,n)}}}async pull(e){if(this.closeRequested||this.cancelRequested||this.completed)throw Error(`pull session is closed`);if(this.unacked)throw Error(`previous chunk is not acknowledged`);if(!Number.isSafeInteger(e.sequence)||e.sequence<0||e.sequence!==this.sequence)throw Error(`pull command sequence mismatch`);if(this.validateHostCredit(e.byteCredit),!this.coordinator.acquire(this.coordinatorOwner))throw Error(`another operation has an unacknowledged package chunk`);let t;try{t=await this.options.driver.pull(e.byteCredit)}catch(e){throw this.coordinator.release(this.coordinatorOwner),e}let n=!1,r=!1,i,a;try{let o=this.options.driver.measureChunk(t),s=this.arrayBufferTransferBytes(t.transfer);if(o<s)throw RangeError(`measured chunk bytes are below ArrayBuffer transfer bytes`);if(a=Math.max(o,s),t.leaseId!==void 0){if(j(t.leaseId,`lease id`),t.retainedBytes===void 0)throw Error(`retained lease bytes are required`);if(this.activeDriverLeases.has(t.leaseId))throw r=!0,Error(`driver returned an active duplicate lease id`);i=this.allocateWireLeaseId(),this.coordinator.retainLease(this.coordinatorOwner,i,t.retainedBytes),this.leases.set(i,{driverLeaseId:t.leaseId,retainedBytes:t.retainedBytes}),this.activeDriverLeases.add(t.leaseId),n=!0}else if(t.retainedBytes!==void 0)throw Error(`retained lease bytes require a lease id`);if(!Number.isSafeInteger(a)||a<0)throw RangeError(`host chunk byte length must be a non-negative safe integer`);if(a>e.byteCredit)throw RangeError(`host chunk exceeds byte credit`)}catch(e){let a;try{await this.options.driver.disposeInvalidChunk?.(t)}catch(e){a=e}if(n&&i!==void 0)try{await this.release(i)}catch(e){a??=e}else if(t.leaseId!==void 0&&!r)try{await this.options.driver.releaseLease?.(t.leaseId)}catch(e){a??=e}if(r)try{await this.cancel()}catch(e){a??=e}throw this.coordinator.release(this.coordinatorOwner),a||e}return this.unacked={sequence:this.sequence,done:t.done},{response:{kind:`chunk`,protocol:A,...this.identity(),requestId:e.requestId,sequence:this.sequence,byteLength:a,done:t.done,payload:t.payload,leaseId:i,usage:this.resourceUsage()},transfer:t.transfer}}async ack(e){if(!Number.isSafeInteger(e)||e<0)throw RangeError(`invalid ack sequence`);if(e<this.sequence)return;if(!this.unacked||e!==this.sequence)throw Error(`ack sequence mismatch`);let t=this.unacked.done;await this.options.driver.acknowledge?.(e),this.unacked=void 0,this.coordinator.release(this.coordinatorOwner),this.sequence++,t&&(this.completed=!0,this.maybeUnregisterCompleted())}async release(e){j(e,`wire lease id`);let t=this.leases.get(e);t&&(await this.options.driver.releaseLease?.(t.driverLeaseId),this.leases.delete(e),this.activeDriverLeases.delete(t.driverLeaseId),this.coordinator.releaseLease(this.coordinatorOwner,e),this.maybeUnregisterCompleted())}async cancel(){if(this.cancelComplete)return;this.cancelRequested=!0,this.unacked=void 0,this.coordinator.release(this.coordinatorOwner);let e;try{await this.releaseAllLeases()}catch(t){e=t}if(!this.driverCancelComplete)try{await this.options.driver.cancel?.(),this.driverCancelComplete=!0}catch(t){e??=t}if(e)throw e;this.cancelComplete=!0,this.unregisterCleanup()}async close(){if(this.closeComplete)return;this.closeRequested=!0,this.unacked=void 0,this.coordinator.release(this.coordinatorOwner);let e;try{await this.releaseAllLeases()}catch(t){e=t}if(!this.driverCloseComplete)try{await this.options.driver.close?.(),this.driverCloseComplete=!0}catch(t){e??=t}if(e)throw e;this.closeComplete=!0,this.unregisterCleanup()}async releaseAllLeases(){let e;for(let t of[...this.leases.keys()])try{await this.release(t)}catch(t){e??=t}if(e)throw e}validateCommandIdentity(e){if(e.protocol!==`ooxml-pull-v1`||e.sessionId!==this.options.sessionId||e.operationId!==this.options.operationId||e.generation!==this.options.generation||!Number.isSafeInteger(e.requestId)||e.requestId<=0)throw Error(`stale or mismatched pull session command`)}validateHostCredit(e){if(j(e,`byte credit`),e>this.options.maxByteCredit)throw RangeError(`byte credit exceeds host maximum`)}accepted(e,t,n=!1){return{kind:`accepted`,protocol:A,...n?{sessionId:e.sessionId,operationId:e.operationId,generation:e.generation}:this.identity(),requestId:e.requestId,command:t,usage:this.resourceUsage()}}identity(){return{sessionId:this.options.sessionId,operationId:this.options.operationId,generation:this.options.generation}}isStaleLifecycle(e){return(e.kind===`cancel`||e.kind===`close`)&&e.protocol===`ooxml-pull-v1`&&Number.isSafeInteger(e.requestId)&&e.requestId>0&&Number.isSafeInteger(e.generation)&&e.generation>0&&e.generation<this.options.generation}sameOperationIdentity(e){return e.sessionId===this.options.sessionId&&e.operationId===this.options.operationId}errorResponse(e,t){return{kind:`error`,protocol:A,sessionId:e.sessionId,operationId:e.operationId,generation:e.generation,requestId:e.requestId,error:t,usage:this.errorResourceUsage()}}async forceFatalCleanup(){this.cancelRequested=!0,this.unacked=void 0,this.coordinator.release(this.coordinatorOwner);let e;for(let t of[...this.leases.keys()])try{await this.release(t)}catch(t){e??=t}if(!this.driverCancelComplete)try{await this.options.driver.cancel?.(),this.driverCancelComplete=!0}catch(t){e??=t}if(e)throw e;this.unregisterCleanup()}allocateWireLeaseId(){if(!Number.isSafeInteger(this.nextWireLeaseId)||this.nextWireLeaseId<=0)throw RangeError(`wire lease id space exhausted`);return this.nextWireLeaseId++}arrayBufferTransferBytes(e){let t=0;for(let n of e??[])if(n instanceof ArrayBuffer&&(t+=n.byteLength,!Number.isSafeInteger(t)))throw RangeError(`ArrayBuffer transfer bytes overflow`);return t}maybeUnregisterCompleted(){this.completed&&this.leases.size===0&&this.unregisterCleanup()}resourceUsage(){return this.options.driver.resourceUsage?.()}errorResourceUsage(){try{return this.resourceUsage()}catch{return}}};i();function Me(e){let t=e instanceof Error?e.message:String(e);if(!t.startsWith(`OOXML_DOCX_ILVL:`))return;let r=t.slice(16);if(r===`repair-required:level-definition`)return new n(`invalid-numbering`,`The DOCX defines a numbering level outside Word’s supported 0–8 range and requires repair.`);if(r===`cannot-open:whitespace`||r===`cannot-open:non-decimal`)return new n(`invalid-numbering`,`Word cannot open this DOCX numbering level (${r.slice(12)}).`)}function N(e){try{return Me(e)??e}catch{return e}}function Ne(e){try{return e()}catch(e){throw N(e)}}var P=class{__destroy_into_raw(){let e=this.__wbg_ptr;return this.__wbg_ptr=0,F.unregister(this),e}free(){let e=this.__destroy_into_raw();Y.__wbg_docxarchive_free(e,0)}acknowledge_document_chunk(e,t,n){let r=Y.docxarchive_acknowledge_document_chunk(this.__wbg_ptr,e,t,n);if(r[1])throw W(r[0])}assert_healthy(){let e=Y.docxarchive_assert_healthy(this.__wbg_ptr);if(e[1])throw W(e[0])}cancel_document_cursor(){Y.docxarchive_cancel_document_cursor(this.__wbg_ptr)}close_document_session(){Y.docxarchive_close_document_session(this.__wbg_ptr)}document_chunk_done(){let e=Y.docxarchive_document_chunk_done(this.__wbg_ptr);if(e[2])throw W(e[1]);return e[0]!==0}document_cursor_resource_usage(){let e=Y.docxarchive_document_cursor_resource_usage(this.__wbg_ptr);if(e[3])throw W(e[2]);let t;return e[0]!==0&&(t=I(e[0],e[1]).slice(),Y.__wbindgen_free(e[0],e[1]*1,1)),t}extract_image(e){let t=U(e,Y.__wbindgen_malloc,Y.__wbindgen_realloc),n=J,r=Y.docxarchive_extract_image(this.__wbg_ptr,t,n);if(r[3])throw W(r[2]);var i=I(r[0],r[1]).slice();return Y.__wbindgen_free(r[0],r[1]*1,1),i}is_picture_part(e){let t=U(e,Y.__wbindgen_malloc,Y.__wbindgen_realloc),n=J,r=Y.docxarchive_is_picture_part(this.__wbg_ptr,t,n);if(r[2])throw W(r[1]);return r[0]!==0}constructor(e,t,n,r){let i=Fe(e,Y.__wbindgen_malloc),a=J,o=Y.docxarchive_new(i,a,!H(t),H(t)?BigInt(0):t,!H(n),H(n)?BigInt(0):n,!H(r),H(r)?BigInt(0):r);if(o[2])throw W(o[1]);return this.__wbg_ptr=o[0]>>>0,F.register(this,this.__wbg_ptr,this),this}open_document_cursor(e,t){let n=Y.docxarchive_open_document_cursor(this.__wbg_ptr,e,t);if(n[1])throw W(n[0])}parse(){let e=Y.docxarchive_parse(this.__wbg_ptr);if(e[3])throw W(e[2]);var t=I(e[0],e[1]).slice();return Y.__wbindgen_free(e[0],e[1]*1,1),t}pull_document_chunk(e,t,n,r){let i=Y.docxarchive_pull_document_chunk(this.__wbg_ptr,e,t,n,r);if(i[3])throw W(i[2]);var a=I(i[0],i[1]).slice();return Y.__wbindgen_free(i[0],i[1]*1,1),a}resource_usage(){let e=Y.docxarchive_resource_usage(this.__wbg_ptr);if(e[3])throw W(e[2]);var t=I(e[0],e[1]).slice();return Y.__wbindgen_free(e[0],e[1]*1,1),t}to_markdown(){let e,t;try{let i=Y.docxarchive_to_markdown(this.__wbg_ptr);var n=i[0],r=i[1];if(i[3])throw n=0,r=0,W(i[2]);return e=n,t=r,z(n,r)}finally{Y.__wbindgen_free(e,t,1)}}};Symbol.dispose&&(P.prototype[Symbol.dispose]=P.prototype.free);function Pe(){return{__proto__:null,\"./docx_parser_bg.js\":{__proto__:null,__wbg___wbindgen_throw_6b64449b9b9ed33c:function(e,t){throw Error(z(e,t))},__wbg_error_a6fa202b58aa1cd3:function(e,t){let n,r;try{n=e,r=t,console.error(z(e,t))}finally{Y.__wbindgen_free(n,r,1)}},__wbg_new_227d7c05414eb861:function(){return Error()},__wbg_stack_3b0d974bbf31e44f:function(e,t){let n=t.stack,r=U(n,Y.__wbindgen_malloc,Y.__wbindgen_realloc),i=J;R().setInt32(e+4,i,!0),R().setInt32(e+0,r,!0)},__wbindgen_cast_0000000000000001:function(e,t){return z(e,t)},__wbindgen_init_externref_table:function(){let e=Y.__wbindgen_externrefs,t=e.grow(4);e.set(0,void 0),e.set(t+0,void 0),e.set(t+1,null),e.set(t+2,!0),e.set(t+3,!1)}}}}const F=typeof FinalizationRegistry>`u`?{register:()=>{},unregister:()=>{}}:new FinalizationRegistry(e=>Y.__wbg_docxarchive_free(e>>>0,1));function I(e,t){return e>>>=0,V().subarray(e/1,e/1+t)}let L=null;function R(){return(L===null||L.buffer.detached===!0||L.buffer.detached===void 0&&L.buffer!==Y.memory.buffer)&&(L=new DataView(Y.memory.buffer)),L}function z(e,t){return e>>>=0,Ie(e,t)}let B=null;function V(){return(B===null||B.byteLength===0)&&(B=new Uint8Array(Y.memory.buffer)),B}function H(e){return e==null}function Fe(e,t){let n=t(e.length*1,1)>>>0;return V().set(e,n/1),J=e.length,n}function U(e,t,n){if(n===void 0){let n=q.encode(e),r=t(n.length,1)>>>0;return V().subarray(r,r+n.length).set(n),J=n.length,r}let r=e.length,i=t(r,1)>>>0,a=V(),o=0;for(;o<r;o++){let t=e.charCodeAt(o);if(t>127)break;a[i+o]=t}if(o!==r){o!==0&&(e=e.slice(o)),i=n(i,r,r=o+e.length*3,1)>>>0;let t=V().subarray(i+o,i+r),a=q.encodeInto(e,t);o+=a.written,i=n(i,r,o,1)>>>0}return J=o,i}function W(e){let t=Y.__wbindgen_externrefs.get(e);return Y.__externref_table_dealloc(e),t}let G=new TextDecoder(`utf-8`,{ignoreBOM:!0,fatal:!0});G.decode();let K=0;function Ie(e,t){return K+=t,K>=2146435072&&(G=new TextDecoder(`utf-8`,{ignoreBOM:!0,fatal:!0}),G.decode(),K=t),G.decode(V().subarray(e,e+t))}const q=new TextEncoder;`encodeInto`in q||(q.encodeInto=function(e,t){let n=q.encode(e);return t.set(n),{read:e.length,written:n.length}});let J=0,Y;function Le(e,t){return Y=e.exports,L=null,B=null,Y.__wbindgen_start(),Y}async function Re(e,t){if(typeof Response==`function`&&e instanceof Response){if(typeof WebAssembly.instantiateStreaming==`function`)try{return await WebAssembly.instantiateStreaming(e,t)}catch(t){if(e.ok&&n(e.type)&&e.headers.get(`Content-Type`)!==`application/wasm`)console.warn(\"`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\\n\",t);else throw t}let r=await e.arrayBuffer();return await WebAssembly.instantiate(r,t)}else{let n=await WebAssembly.instantiate(e,t);return n instanceof WebAssembly.Instance?{instance:n,module:e}:n}function n(e){switch(e){case`basic`:case`cors`:case`default`:return!0}return!1}}async function ze(e){if(Y!==void 0)return Y;e!==void 0&&(Object.getPrototypeOf(e)===Object.prototype?{module_or_path:e}=e:console.warn(`using deprecated parameters for the initialization function; pass a single object instead`));let t=Pe();(typeof e==`string`||typeof Request==`function`&&e instanceof Request||typeof URL==`function`&&e instanceof URL)&&(e=fetch(e));let{instance:n,module:r}=await Re(await e,t);return Le(n,r)}async function Be(e){return Y=void 0,L=null,B=null,ze(e)}function Ve(e){let t=e(e=>e.document_cursor_resource_usage?.());return t?se(t):void 0}const He=67108864;var Ue=class{archive;coordinator=new M;host=null;identity=null;executeArchive;constructor(e,t=e=>e(this.requireArchive())){this.archive=e,this.executeArchive=e=>Ne(()=>t(e))}open(e){if(this.host)throw Error(`a DOCX document pull session is already active`);this.executeArchive(t=>{t.open_document_cursor(e.operationId,e.generation)});let t=0;this.identity=e,this.host=new je({...e,maxByteCredit:He,coordinator:this.coordinator,driver:{pull:n=>{let r;try{r=this.executeArchive(r=>r.pull_document_chunk(t,e.operationId,e.generation,n))}catch(e){throw ae(e,n,He)||e}let i=Oe(r);return{payload:i,byteLength:i.byteLength,done:this.executeArchive(e=>e.document_chunk_done()),transfer:[i]}},measureChunk:({payload:e})=>e.byteLength,acknowledge:n=>{if(n!==t)throw Error(`DOCX document acknowledgement sequence mismatch`);this.executeArchive(n=>n.acknowledge_document_chunk(t,e.operationId,e.generation)),t+=1},cancel:()=>this.executeArchive(e=>e.cancel_document_cursor()),close:()=>this.executeArchive(e=>e.close_document_session()),resourceUsage:()=>Ve(this.executeArchive)}})}dispatch(e,t){return!this.host||!this.identity?(t({protocol:A,kind:`error`,sessionId:e.sessionId,operationId:e.operationId,generation:e.generation,requestId:e.requestId,error:O(Error(`DOCX document pull session is not open`))}),Promise.resolve()):this.host.dispatch(e,t)}async reset(){if(this.host)try{this.archive()&&this.executeArchive(e=>e.close_document_session())}finally{this.host=null,this.identity=null,this.coordinator=new M}}requireArchive(){let e=this.archive();if(!e)throw Error(`No docx loaded`);return e}};function We(e){return!!e&&typeof e==`object`&&e.protocol===`ooxml-pull-v1`}const X=new Ee(ze,{freeArchive:e=>e.free(),reinit:Be}),Z=new Ue(()=>X.archive,e=>X.run(()=>{let t=X.archive;if(!t)throw Error(`No docx loaded`);return e(t)}));let Q=0;const $=(e,t)=>self.postMessage(e,t);self.onmessage=async e=>{let n=e.data;if(We(n)){try{await Z.dispatch(n,$)}catch(e){$({protocol:A,kind:`error`,sessionId:n.sessionId,operationId:n.operationId,generation:n.generation,requestId:n.requestId,error:O(N(e))})}return}if(n.type===`init`){X.setWasmInput(t(n.wasmUrl)??n.wasmUrl);return}let r=n.id;try{if(await X.ensureReady(),n.type!==`parse`&&X.archive){let e=X.archive;X.run(()=>e.assert_healthy())}if(n.type===`parse`){await Z.reset();let[e,t,i]=ke(n.resourcePolicy),a=new Uint8Array(n.data);X.run(()=>{let n=new P(a,e,t,i);X.setArchive(n)}),Q+=1;let o={sessionId:Q,operationId:Q,generation:Q};Z.open(o),$({type:`documentSessionOpened`,id:r,...o});return}let e=X.archive;if(n.type===`extractImage`){if(!e)throw Error(`No docx loaded`);let t=X.run(()=>e.extract_image(n.path).buffer),i={type:`imageExtracted`,id:r,bytes:t};self.postMessage(i,[t]);return}if(n.type===`resourceUsage`){if(!e)throw Error(`No docx loaded`);$({type:`resourceUsage`,id:r,usage:se(X.run(()=>e.resource_usage()))});return}if(n.type===`toMarkdown`){if(!e)throw Error(`No docx loaded`);$({type:`markdownRendered`,id:r,markdown:X.run(()=>e.to_markdown())});return}}catch(e){$({type:`error`,id:r,...O(N(e))})}};", st = typeof self < "u" && self.Blob && new Blob(["URL.revokeObjectURL(import.meta.url);", ot], { type: "text/javascript;charset=utf-8" });
function ct(e) {
	let t;
	try {
		if (t = st && (self.URL || self.webkitURL).createObjectURL(st), !t) throw "";
		let n = new Worker(t, {
			type: "module",
			name: e?.name
		});
		return n.addEventListener("error", () => {
			(self.URL || self.webkitURL).revokeObjectURL(t);
		}), n;
	} catch {
		return new Worker("data:text/javascript;charset=utf-8," + encodeURIComponent(ot), {
			type: "module",
			name: e?.name
		});
	}
}
var lt = new URL("docx_parser_bg.wasm", import.meta.url).href;
function ut(e) {
	return e === "nativeRouteSentinels" ? "[ooxml] mode: 'worker' fell back to main-thread rendering because the worker cannot register the font probes that size absent-font lines." : "[ooxml] mode: 'worker' fell back to main-thread rendering because this document requires DOM OpenType vertical glyph selection.";
}
function dt(e) {
	let t = /* @__PURE__ */ new Map();
	for (let n of e.pages) for (let e of n.bookmarkStarts) e.name !== "" && !t.has(e.name) && t.set(e.name, n.pageIndex);
	return t;
}
var ft = new Uint32Array([
	1116352408,
	1899447441,
	3049323471,
	3921009573,
	961987163,
	1508970993,
	2453635748,
	2870763221,
	3624381080,
	310598401,
	607225278,
	1426881987,
	1925078388,
	2162078206,
	2614888103,
	3248222580,
	3835390401,
	4022224774,
	264347078,
	604807628,
	770255983,
	1249150122,
	1555081692,
	1996064986,
	2554220882,
	2821834349,
	2952996808,
	3210313671,
	3336571891,
	3584528711,
	113926993,
	338241895,
	666307205,
	773529912,
	1294757372,
	1396182291,
	1695183700,
	1986661051,
	2177026350,
	2456956037,
	2730485921,
	2820302411,
	3259730800,
	3345764771,
	3516065817,
	3600352804,
	4094571909,
	275423344,
	430227734,
	506948616,
	659060556,
	883997877,
	958139571,
	1322822218,
	1537002063,
	1747873779,
	1955562222,
	2024104815,
	2227730452,
	2361852424,
	2428436474,
	2756734187,
	3204031479,
	3329325298
]);
function pt(e) {
	let t = new Uint32Array([
		1779033703,
		3144134277,
		1013904242,
		2773480762,
		1359893119,
		2600822924,
		528734635,
		1541459225
	]), n = new Uint32Array(64), r = Math.ceil((e.length + 9) / 64) * 64, i = e.length * 8, a = (t) => t < e.length ? e[t] : t === e.length ? 128 : t >= r - 8 ? Math.floor(i / 2 ** ((r - t - 1) * 8)) & 255 : 0, o = (e, t) => e >>> t | e << 32 - t;
	for (let e = 0; e < r; e += 64) {
		for (let t = 0; t < 16; t++) {
			let r = e + t * 4;
			n[t] = a(r) << 24 | a(r + 1) << 16 | a(r + 2) << 8 | a(r + 3);
		}
		for (let e = 16; e < 64; e++) {
			let t = n[e - 15], r = n[e - 2], i = o(t, 7) ^ o(t, 18) ^ t >>> 3, a = o(r, 17) ^ o(r, 19) ^ r >>> 10;
			n[e] = n[e - 16] + i + n[e - 7] + a >>> 0;
		}
		let [r, i, s, c, l, u, d, f] = t;
		for (let e = 0; e < 64; e++) {
			let t = o(l, 6) ^ o(l, 11) ^ o(l, 25), a = l & u ^ ~l & d, p = f + t + a + ft[e] + n[e] >>> 0, m = (o(r, 2) ^ o(r, 13) ^ o(r, 22)) + (r & i ^ r & s ^ i & s) >>> 0;
			f = d, d = u, u = l, l = c + p >>> 0, c = s, s = i, i = r, r = p + m >>> 0;
		}
		t[0] = t[0] + r >>> 0, t[1] = t[1] + i >>> 0, t[2] = t[2] + s >>> 0, t[3] = t[3] + c >>> 0, t[4] = t[4] + l >>> 0, t[5] = t[5] + u >>> 0, t[6] = t[6] + d >>> 0, t[7] = t[7] + f >>> 0;
	}
	let s = new Uint8Array(32), c = new DataView(s.buffer);
	return t.forEach((e, t) => c.setUint32(t * 4, e)), s;
}
var mt = a, ht = 64, z = 2;
async function gt(e, t) {
	let n;
	try {
		n = globalThis.crypto?.subtle ? new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256", e.slice().buffer)) : pt(e);
	} catch {
		n = pt(e);
	}
	let r = Array.from(n, (e) => e.toString(16).padStart(2, "0")).join(""), i = 2166136261;
	for (let e of t.trim().toLowerCase()) i ^= e.codePointAt(0), i = Math.imul(i, 16777619);
	return `__ooxml_docx_embedded_${r}_${(i >>> 0).toString(16)}`;
}
async function _t(e, n) {
	let r = e.embeddedFonts;
	if (!r || r.length === 0) return {
		faces: [],
		metrics: {},
		routes: []
	};
	let i = e.settings, a = [], u = /* @__PURE__ */ new Set();
	for (let e of r) {
		let t = vt(e.style) === "bold" ? 700 : 400, n = yt(e.style), r = `${m(e.fontName)}:${t}:${n}`;
		u.has(r) || (u.add(r), a.push(e));
	}
	let d = [], f = 0, p = Math.min(a.length, ht), h = a.length - p;
	for (let e = 0; e < p; e += z) {
		let r = a.slice(e, Math.min(e + z, p)), o = await Promise.all(r.map(async (e) => {
			try {
				return await n(e.partPath);
			} catch (e) {
				if (e instanceof t || te(e)) throw e;
				let n = he(e);
				if (n) throw n;
				return null;
			}
		}));
		for (let e = 0; e < r.length; e++) {
			let t = r[e], n = o[e];
			if (n) {
				if (!s(n) || n.byteLength > mt - f) {
					h++;
					continue;
				}
				try {
					let e = t.partPath.toLowerCase().endsWith(".odttf") ? l(n, t.fontKey ?? "") : n, r = await gt(e, t.fontName), a = {
						family: r,
						bytes: e,
						odttf: !1,
						fontKey: "",
						weight: vt(t.style),
						style: yt(t.style)
					}, o = null;
					try {
						let n = ee(e), s = i?.__libreOfficeLineBoxes === !0, c = n?.farEastCodePage == null || s ? null : y({
							...n,
							farEastCodePage: n.farEastCodePage
						}), l = n && s ? E(n, void 0) : void 0;
						(c || l || n?.averageCharWidthRatio != null) && (o = Object.freeze({
							family: r,
							requestedFamily: t.fontName,
							weight: a.weight === "bold" ? 700 : 400,
							style: a.style,
							sourceIdentity: `embedded:${r}`,
							synthesized: !1,
							...c ? {
								farEastCodePage: n.farEastCodePage,
								lineHeightRatio: c.lineHeightRatio,
								designAscentRatio: c.designAscentRatio,
								designDescentRatio: c.designDescentRatio
							} : l ?? {},
							...n?.averageCharWidthRatio == null ? {} : { averageCharWidthRatio: n.averageCharWidthRatio },
							unicodeRanges: n?.unicodeRanges ?? [],
							...c && n?.hasEastAsianCmap ? { eastAsianLineHeightRatio: c.lineHeightRatio } : {}
						}));
					} catch {}
					d.push({
						face: a,
						metric: o,
						route: {
							requestedFamily: t.fontName,
							resolvedFamily: a.family,
							weight: a.weight === "bold" ? 700 : 400,
							style: a.style,
							resourceIdentity: `embedded:${a.family}`
						}
					}), f += n.byteLength;
				} catch {
					continue;
				}
			}
		}
	}
	let g = Object.freeze(h > 0 ? [Object.freeze({
		code: "MISSING_RESOURCE",
		severity: "warning",
		message: `Skipped ${h} embedded font face(s) under the document font resource limits; fallback fonts are used`
	})] : []), _ = d;
	if (_.length === 0) return {
		faces: [],
		metrics: {},
		routes: [],
		diagnostics: g
	};
	let v = [], b = /* @__PURE__ */ new Set();
	try {
		for (let e = 0; e < _.length; e += z) {
			let t = _.slice(e, e + z);
			for (let e of await c(t.map((e) => e.face))) b.has(e) ? o([e]) : (b.add(e), v.push(e));
		}
	} catch (e) {
		throw o(v), e;
	}
	let x = new Set(v.map((e) => {
		let t = e.family.trim().replace(/^(['"])(.*)\1$/, "$2"), n = e.weight === "bold" ? 700 : Number(e.weight) || 400, r = e.style === "italic" ? "italic" : "normal";
		return `${m(t)}:${n}:${r}`;
	})), S = Object.create(null), C = [];
	for (let e of _) {
		let t = m(e.face.family), n = e.face.weight === "bold" ? 700 : 400, r = e.face.style, i = `${t}:${n}:${r}`;
		if (!x.has(i) || (C.push(Object.freeze(e.route)), !e.metric)) continue;
		let a = m(e.route.requestedFamily);
		S[n === 400 && r === "normal" ? a : `${a}:${n}:${r}`] = e.metric;
	}
	return {
		faces: v,
		metrics: Object.freeze(S),
		routes: Object.freeze(C),
		diagnostics: g
	};
}
function vt(e) {
	return e === "bold" || e === "boldItalic" ? "bold" : "normal";
}
function yt(e) {
	return e === "italic" || e === "boldItalic" ? "italic" : "normal";
}
var bt = pe, xt = 16384;
function St(e, t) {
	let n = [], r = 0, i = !1;
	for (let a of e) {
		if (a.length === 0) continue;
		if (r > 0) {
			if (r >= t) {
				i = !0;
				break;
			}
			n.push("\n"), r++;
		}
		let e = De(a, Math.max(0, t - r));
		if (n.push(e), r += e.length, e.length < a.length) {
			i = !0;
			break;
		}
	}
	let a = n.join("");
	return {
		...a.length === 0 ? {} : { text: a },
		truncated: i
	};
}
function* B(e) {
	if (e.kind === "paragraph") {
		for (let t of e.lines) {
			let e = t.placements.flatMap((e) => e.kind === "text" && !e.optionalHyphenGlyph ? [e.text] : []).join("");
			e && (yield e);
		}
		return;
	}
	if (e.kind === "table") {
		for (let t of e.rows) for (let e of t.cells) for (let t of e.blocks) yield* B(t.layout);
		return;
	}
	if (e.kind === "note") {
		e.leading?.paragraph && (yield* B(e.leading.paragraph));
		for (let t of e.story.blocks) yield* B(t);
		e.trailing?.paragraph && (yield* B(e.trailing.paragraph));
	} else if (e.kind === "textbox") for (let t of e.story.blocks) yield* B(t);
}
function* Ct(e) {
	for (let t of e.drawing.commands) (t.kind === "text" || t.kind === "watermark-text") && (yield t.text);
	for (let t of e.textBoxes) yield* B(t);
}
function wt(e) {
	let t = e ?? xt;
	if (!Number.isFinite(t) || t < 0) throw RangeError("maxTextCharacters must be a finite non-negative number.");
	return Math.min(bt, Math.floor(t));
}
function Tt(e) {
	return {
		story: e.story,
		storyInstance: e.storyInstance,
		path: [...e.path]
	};
}
function Et(e) {
	return "drawing" in e ? e.drawing.inkBounds : e.placement.bounds;
}
function Dt(e) {
	let t = Et(e), n = [
		h(e.pointToPage, t),
		h(e.pointToPage, {
			xPt: t.xPt + t.widthPt,
			yPt: t.yPt
		}),
		h(e.pointToPage, {
			xPt: t.xPt,
			yPt: t.yPt + t.heightPt
		}),
		h(e.pointToPage, {
			xPt: t.xPt + t.widthPt,
			yPt: t.yPt + t.heightPt
		})
	], r = Math.min(...n.map((e) => e.xPt)), i = Math.min(...n.map((e) => e.yPt)), a = Math.max(...n.map((e) => e.xPt)), o = Math.max(...n.map((e) => e.yPt));
	return {
		xPt: r,
		yPt: i,
		widthPt: a - r,
		heightPt: o - i
	};
}
function V(e, t) {
	return t.xPt >= e.xPt && t.xPt <= e.xPt + e.widthPt && t.yPt >= e.yPt && t.yPt <= e.yPt + e.heightPt;
}
function Ot(e, t) {
	let n = !1;
	for (let r = 0, i = t.length - 1; r < t.length; i = r++) {
		let a = t[r], o = t[i];
		a.yPt > e.yPt != o.yPt > e.yPt && e.xPt < (o.xPt - a.xPt) * (e.yPt - a.yPt) / (o.yPt - a.yPt) + a.xPt && (n = !n);
	}
	return n;
}
function kt(e, t) {
	return V(e.inkBounds, t) ? e.clip ? e.clip.kind === "rect" ? V(e.clip.rect, t) : Ot(t, e.clip.points) : !0 : !1;
}
function At(e, t, n) {
	for (let n of e.clips) {
		let e = p(n.pointToPage, t);
		if (!e || !V(n.bounds, e)) return !1;
	}
	return "drawing" in e ? kt(e.drawing, n) : V(e.placement.bounds, n);
}
function H(e, t) {
	return e.commands.find((e) => e.kind === "resource" && e.resourceKind === t);
}
function jt(e) {
	return H(e, "chart") ? "chart" : e.commands.some((e) => e.kind === "drawingml-shape" || e.kind === "drawingml-image-fill" || e.kind === "fill-rect" || e.kind === "stroke-rect" || e.kind === "text" || e.kind === "watermark-text") ? "shape" : H(e, "image") ? "image" : null;
}
function Mt(e, t, n, r, i, a) {
	let o = "drawing" in e ? jt(e.drawing) : e.placement.resourceKind;
	if (!o) return null;
	let s, c = !1, l, u;
	if (o === "chart") {
		let t = "drawing" in e ? H(e.drawing, "chart").resourceKey : e.placement.resourceKey, n = i.resolve(t, "chart"), r = ue(n.model, a);
		s = r.text, c = r.truncated, u = n.model.series.length;
	} else if (o === "image") {
		let t = "drawing" in e ? H(e.drawing, "image").resourceKey : e.placement.resourceKey, n = i.descriptors.find((e) => e.resourceKey === t && e.kind === "image" && "mimeType" in e);
		if (!n) throw Error(`Unknown image paint resource: ${t}`);
		l = n.mimeType;
	} else {
		let t = St(Ct(e), a);
		s = t.text, c = t.truncated;
	}
	return {
		format: "docx",
		kind: "element",
		pageIndex: t,
		elementIndex: n,
		elementType: o,
		point: { ...r },
		bounds: Dt(e),
		source: Tt("drawing" in e ? e.drawing.source : e.source),
		...s === void 0 ? {} : { text: s },
		...l === void 0 ? {} : { mimeType: l },
		...u === void 0 ? {} : { seriesCount: u },
		truncated: c,
		truncationReasons: c ? ["text"] : [],
		textCharacters: s?.length ?? 0,
		maxTextCharacters: a
	};
}
function Nt(e, t, n, r, i = {}) {
	if (!Number.isFinite(n.xPt) || !Number.isFinite(n.yPt)) throw RangeError("DOCX hit-test point must contain finite page coordinates.");
	let a = wt(i.maxTextCharacters), o = Je(e, t);
	for (let e = o.length - 1; e >= 0; e--) {
		let i = o[e], s = p(i.pointToPage, n);
		if (!s || !At(i, n, s)) continue;
		let c = Mt(i, t, e, n, r, a);
		if (c) return c;
	}
	return null;
}
function Pt(e, t, n, r) {
	return Nt(qe(e, {
		currentDate: r.currentDate,
		defaultCurrentDateMs: r.defaultCurrentDateMs,
		showTrackedChanges: r.showTrackedChanges
	}, t).layout, t, n, _(e), r);
}
function Ft(e, t) {
	let n = wt(t), r = e.text === void 0 ? void 0 : De(e.text, n), i = e.truncated || e.text !== void 0 && r.length < e.text.length;
	return {
		...structuredClone(e),
		...r === void 0 ? {} : { text: r },
		truncated: i,
		truncationReasons: i ? ["text"] : [],
		textCharacters: r?.length ?? 0,
		maxTextCharacters: n
	};
}
function U(e) {
	let t = Ye(e.id);
	return t === void 0 ? void 0 : `${e.kind}\u0000${t}`;
}
function W(e) {
	return Object.freeze({
		...e,
		path: Object.freeze([...e.path])
	});
}
function It(e, t) {
	return e !== void 0 && e.story === t.story && e.storyInstance === t.storyInstance && e.path.length === t.path.length && e.path.every((e, n) => e === t.path[n]);
}
function G(e, t) {
	let n = 0, r = e.length;
	for (; n < r;) {
		let i = n + Math.floor((r - n) / 2);
		e[i] < t ? n = i + 1 : r = i;
	}
	return n;
}
function Lt(e, t) {
	let n = Array(e.length), r;
	for (let i = e.length - 1; i >= 0; --i) {
		n[i] = r;
		let a = e[i], o = t.get(I(a.source))?.[0];
		o !== void 0 && (r = Object.freeze({
			source: W(a.source),
			sourceRunIndex: o
		}));
	}
	let i = Array(e.length), a;
	for (let n = 0; n < e.length; n += 1) {
		i[n] = a;
		let r = e[n], o = t.get(I(r.source))?.at(-1);
		o !== void 0 && (a = Object.freeze({
			source: W(r.source),
			sourceRunIndex: o
		}));
	}
	return {
		following: n,
		preceding: i
	};
}
function Rt(e, t, n, r, i, a) {
	let o = r[e], s = i.get(I(o.source)) ?? [], c = s[G(s, n)], l = s[G(s, t) - 1], u = c ?? l;
	return u === void 0 ? a.following[e] ?? a.preceding[e] : Object.freeze({
		source: W(o.source),
		sourceRunIndex: u
	});
}
function zt(e, t, n = /* @__PURE__ */ new Map()) {
	let r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Set();
	e.forEach((e, t) => {
		let n = U(e);
		n === void 0 || i.has(n) || (r.has(n) ? (r.delete(n), i.add(n)) : r.set(n, t));
	});
	let a = t.blocks.sources.flatMap((e) => {
		if (e.story !== "body") return [];
		let n = t.blocks.resolve(e);
		return n.type === "paragraph" ? [{
			source: e,
			runs: n.runs
		}] : [];
	}), o = new Map([...n].map(([e, t]) => [e, Object.freeze([...t].sort((e, t) => e - t))])), s = Lt(a, o), c = [];
	for (let [e, t] of a.entries()) {
		let n = 0;
		for (; n < t.runs.length;) {
			let i = t.runs[n], l = i.revision?.kind ? U({
				kind: i.revision.kind,
				id: i.revision.id
			}) : void 0, u = l === void 0 ? void 0 : r.get(l);
			if (u === void 0) {
				n += 1;
				continue;
			}
			let d = n;
			for (n += 1; n < t.runs.length;) {
				let e = t.runs[n].revision;
				if (!e?.kind || U({
					kind: e.kind,
					id: e.id
				}) !== l) break;
				n += 1;
			}
			let f = n, p = o.get(I(t.source)) ?? [], m = (p[G(p, d)] ?? f) < f ? void 0 : Rt(e, d, f, a, o, s);
			c.push(Object.freeze({
				revisionIndex: u,
				source: W(t.source),
				startRunIndex: d,
				endRunIndex: f,
				...m === void 0 ? {} : { geometryFallback: m }
			}));
		}
	}
	return c;
}
function Bt(e, t, n = /* @__PURE__ */ new Map(), r = {}) {
	if ((e?.length ?? 0) === 0) return [];
	let i = zt(e ?? [], t, n), a = r.completedSourceKeys;
	return a === void 0 ? i : i.filter((e) => {
		let t = n.get(I(e.source));
		return t !== void 0 && [...t].some((t) => t >= e.startRunIndex && t < e.endRunIndex) || a.has(I(e.source));
	});
}
function Vt(e, t) {
	let n = t.filter((t) => t.sourceRunIndex !== void 0 && It(t.source, e.source) && t.sourceRunIndex >= e.startRunIndex && t.sourceRunIndex < e.endRunIndex);
	if (n.length > 0) return n;
	let r = e.geometryFallback;
	return r === void 0 ? [] : t.filter((e) => e.sourceRunIndex === r.sourceRunIndex && It(e.source, r.source));
}
var Ht = 12;
async function Ut(e, t, n, r = {}) {
	let { onPreview: i, scheduler: a } = r;
	return Pe(Ke(e, t, n, i && e.sequence.length > Ht ? { onPages: (e, t) => {
		i(Object.freeze({
			layout: e,
			exact: !1,
			coveredEntries: t
		}));
	} } : void 0), a);
}
var K = /* @__PURE__ */ new WeakMap();
function q(e, t) {
	let n = Object.freeze({ ...t });
	for (let t of [...K.get(e) ?? []]) try {
		t.notify(n);
	} catch (e) {
		try {
			t.report(e);
		} catch {}
	}
}
function Wt(e, t, n, r) {
	let i = K.get(e);
	i || (i = /* @__PURE__ */ new Set(), K.set(e, i));
	let a = Object.freeze({
		notify: n,
		report: r
	});
	i.add(a);
	try {
		n(Object.freeze({ ...t() }));
	} catch (e) {
		try {
			r(e);
		} catch {}
	}
	return () => {
		i?.delete(a), i?.size === 0 && K.delete(e);
	};
}
function Gt(e, t) {
	if (!e) return 0;
	let n = Math.min(e.length, t.length), r = 0;
	for (; r < n && J(e[r], t[r]);) r += 1;
	return r;
}
function J(e, t) {
	if (e === t) return !0;
	if (typeof e != "object" || typeof t != "object" || e === null || t === null) return !1;
	if (Array.isArray(e)) {
		if (!Array.isArray(t) || e.length !== t.length) return !1;
		for (let n = 0; n < e.length; n += 1) if (!J(e[n], t[n])) return !1;
		return !0;
	}
	if (Array.isArray(t)) return !1;
	let n = Object.keys(e);
	if (n.length !== Object.keys(t).length) return !1;
	for (let r of n) if (!Object.prototype.hasOwnProperty.call(t, r) || !J(e[r], t[r])) return !1;
	return !0;
}
var Y = /* @__PURE__ */ new WeakMap(), Kt = /* @__PURE__ */ new WeakMap(), qt = Symbol("docxLayoutViewRequester");
function X(e) {
	let t = b(e), n = t.activeLayoutOptions;
	return {
		showTrackedChanges: n?.showTrackedChanges === !0,
		currentDate: n?.currentDateMs ?? t.defaultCurrentDateMs
	};
}
async function Jt(e, t, n) {
	let r = b(e), i = M(t.currentDate, r.defaultCurrentDateMs, t.showTrackedChanges === !0), a = Object.freeze({
		showTrackedChanges: i.showTrackedChanges === !0,
		currentDate: i.currentDateMs
	}), o = {
		showTrackedChanges: a.showTrackedChanges,
		currentDate: a.currentDate,
		[qt]: n
	};
	await e.setLayoutView(o);
	let s = X(e);
	return s.currentDate === a.currentDate && s.showTrackedChanges === a.showTrackedChanges;
}
async function Yt(e, t, n, r, i) {
	let a = !1, o = () => {
		a || (a = !0, e.destroy());
	};
	try {
		for (; !t.aborted;) {
			let a = n();
			if (a === void 0 || X(e).showTrackedChanges === a) break;
			t.addEventListener("abort", o, { once: !0 });
			try {
				await Jt(e, {
					showTrackedChanges: a,
					currentDate: r()
				}, i);
			} finally {
				t.removeEventListener("abort", o);
			}
		}
	} catch (e) {
		throw o(), e;
	}
}
function Xt(e, t) {
	let n = Object.freeze({ ...X(e) }), r = (Kt.get(e) ?? 0) + 1;
	Kt.set(e, r);
	let i = Object.freeze({
		view: n,
		generation: r,
		requester: t
	});
	for (let t of [...Y.get(e) ?? []]) try {
		t.notify(i);
	} catch (e) {
		try {
			t.report(e);
		} catch {}
	}
}
function Zt(e, t, n) {
	let r = Y.get(e);
	r || (r = /* @__PURE__ */ new Set(), Y.set(e, r));
	let i = Object.freeze({
		notify: t,
		report: n
	});
	return r.add(i), () => {
		r?.delete(i), r?.size === 0 && Y.delete(e);
	};
}
function Qt() {
	return new Te(() => "document", () => 0);
}
function Z(e) {
	return we(e, Qt);
}
function $t(e) {
	return e.partFailures, Z(e);
}
function en(e) {
	return e.legacyDoc !== void 0 || e.odt !== void 0;
}
var Q = Symbol("docxViewerLoadSignal");
function tn(e, t) {
	return e !== null && e.currentDateMs === t.currentDateMs && e.showTrackedChanges === !0 == (t.showTrackedChanges === !0);
}
var nn = Object.freeze([]), rn = Object.freeze([]), an = Object.freeze({
	comments: Object.freeze([]),
	revisions: Object.freeze([])
});
function $(e, t) {
	return g({
		comments: e,
		revisions: t
	}, "DOCX review metadata");
}
var on = class e {
	get diagnostics() {
		return g([
			...this._mode === "worker" ? this._meta?.diagnostics ?? [] : this._getLayout()?.diagnostics ?? [],
			...this._meta?.resourceDiagnostics ?? [],
			...at(this)
		], "DOCX diagnostics");
	}
	get partFailures() {
		return this._partFailureLog.list;
	}
	get _partFailureLog() {
		let e = Z(this), t = this._source?.fatalParse?.message ?? this._meta?.partFailure?.message;
		return t !== void 0 && e.size === 0 && e.add({
			kind: "document",
			message: t
		}), e;
	}
	_errorPlaceholderText(e) {
		let t = Ee(e);
		if (t.kind === "none") return;
		let n = this._partFailureLog.get("document");
		if (!n) return;
		let r = Se(t, n);
		return r === null ? void 0 : Ce(r);
	}
	_metrics = null;
	_cjkFallback = "jp";
	_allowFootnoteContinuation = !1;
	_document = null;
	_source = null;
	_meta = null;
	_review = an;
	_layoutLifecycle = new Ae();
	_layoutObservers = new ke();
	_layoutCompletion = null;
	_layoutAbort = null;
	_bookmarkPages = null;
	_commentAnchorRanges = null;
	_revisionAnchorRanges = null;
	_reviewProjectionIndex = null;
	_parseRequestId = null;
	_progressive = null;
	_parseWatchdog;
	_parseWatchdogMs;
	_layoutViewGeneration = 0;
	_mode = "main";
	_threeD;
	_regionMap;
	_chartEx;
	_tiff;
	_worker;
	_bridge;
	_rawParts = new Oe({
		maxEntries: 64,
		maxBytes: a
	});
	_embeddedFontFaces = [];
	_officeFontFaces = [];
	_mainThreadFallbackReason = "vertical";
	_nativeRouteFaces = [];
	_nativeRouteFacesReleased = !1;
	_fontSourceSession = null;
	_fontResolverBridge = null;
	_chartFontSubstitutions;
	_fetchImage = (e, t) => this.getImage(e, t);
	constructor(e, t, n, r) {
		this._worker = e, this._mode = t, T(this, n), this._bridge = new ce(this._worker, {
			correlate: (e) => "protocol" in e && e.protocol === "ooxml-pull-v1" ? e.requestId : "id" in e ? e.id : void 0,
			onUnsolicited: (e) => this._onWorkerLayoutPush(e),
			toError: (e) => {
				if (!("protocol" in e || e.type !== "error")) return Object.assign(me(e), {
					...e.reason === void 0 ? {} : { reason: e.reason },
					...e.outgoingColumnIndex === void 0 ? {} : { outgoingColumnIndex: e.outgoingColumnIndex },
					...e.outgoingColumnCount === void 0 ? {} : { outgoingColumnCount: e.outgoingColumnCount },
					...e.incomingColumnCount === void 0 ? {} : { incomingColumnCount: e.incomingColumnCount }
				});
			}
		});
		let i = new URL(r ?? lt, be()).href;
		this._bridge.post({
			type: "init",
			wasmUrl: i
		});
	}
	static async load(t, a = {}) {
		let s = a[Q];
		a = Object.assign(de(a), s ? { [Q]: s } : {});
		let c = s?.signal, l = () => {
			if (c?.aborted) throw new N();
		};
		if (l(), a.legacyDoc !== void 0 || a.odt !== void 0) {
			let { loadDocxModelSource: e } = await import("./document-model-source-BiUiDUeg.js"), n = await e(t, a, s);
			if (c?.aborted) throw n.destroy(), new N();
			return n;
		}
		let u = k(a.cjkFallback), f = ge(a), p = Date.now(), m = a.mode ?? "main";
		m === "main" && a.fonts && import("./font-source-load-DtHoLLYl.js").catch(() => void 0);
		let h = new _e({
			enabled: !0,
			format: "docx",
			mode: m,
			policy: f.policy,
			onMetrics: f.onResourceMetrics,
			emitToConsole: f.debug
		});
		try {
			if (m === "worker" && (typeof Worker > "u" || typeof OffscreenCanvas > "u")) throw Error("mode: 'worker' requires Worker and OffscreenCanvas support");
			let g;
			if (typeof t == "string") {
				let e = await fetch(t, { signal: c });
				if (!e.ok) throw Error(`Failed to fetch: ${e.status} ${e.statusText}`);
				g = await e.arrayBuffer();
			} else g = t;
			l(), g = n(await r(g, a.password)), l(), h.setSourceBytes(g.byteLength), h.checkpoint("container ready");
			let _ = m === "worker" ? (await import("./render-worker-host-BPvvLDas.js")).createRenderWorker() : new ct(), v = m === "worker" ? se(a) : void 0, y = m === "worker" && !!a.progressiveLayout, C, w = !1, T = () => {
				w || !C || (w = !0, C.destroy());
			};
			try {
				C = new e(_, m, p, a.wasmUrl), c?.addEventListener("abort", T, { once: !0 }), l(), C._metrics = h, C._cjkFallback = u, C._allowFootnoteContinuation = a.allowFootnoteContinuation !== !1;
				let t = b(C), n = M(a.currentDate, t.defaultCurrentDateMs, a.showTrackedChanges === !0);
				t.activeLayoutOptions = n, await C._parse(g, f.policy, m === "worker" ? j(a.fonts) : void 0, a.workerTimeoutMs, (e) => h.observeUsage(e), v, y ? {
					onPartial: a.onLayoutPartial,
					onComplete: a.onLayoutComplete,
					onProgress: a.onLayoutProgress,
					layoutOptions: n,
					abort: new AbortController(),
					firstPublication: je(),
					published: !1,
					settled: !1
				} : void 0), l(), m === "worker" && C._mode === "main" && (h.setMode("main"), console.warn(ut(C._mainThreadFallbackReason))), a.math && C._mode === "worker" && !v?.math && console.warn("[ooxml] a custom math renderer cannot cross the worker boundary; equations will be skipped in mode: 'worker'. Use the math renderer from @silurus/ooxml/math."), a.threeD && C._mode === "worker" && !v?.threeD && console.warn("[ooxml] a custom 3-D chart renderer cannot cross the worker boundary; charts use their 2-D family fallback in mode: 'worker'. Use the renderer from @silurus/ooxml/three-d."), C._threeD = C._mode === "worker" ? void 0 : a.threeD, a.regionMap && C._mode === "worker" && !v?.regionMap && console.warn("[ooxml] a custom Region Map renderer cannot cross the worker boundary; geospatial charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/region-map."), C._regionMap = C._mode === "worker" ? void 0 : a.regionMap, a.chartEx && C._mode === "worker" && !v?.chartEx && console.warn("[ooxml] a custom ChartEx renderer cannot cross the worker boundary; ChartEx charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/chart-ex."), C._chartEx = C._mode === "worker" ? void 0 : a.chartEx, a.tiff && C._mode === "worker" && !v?.tiff && console.warn("[ooxml] a custom TIFF codec cannot cross the worker boundary; recognized TIFF images will use an unavailable-image placeholder in mode: 'worker'. Use the codec from @silurus/ooxml/tiff to display them."), C._tiff = C._mode === "worker" ? void 0 : a.tiff;
				let r, w, E = C, D = C._mode === "main" && C._document && C._source ? Ve(Ge(C._source, C._document, {
					fontSubstitutes: x(j(a.fonts)),
					cjkFallback: u
				}), !0).then((e) => E._nativeRouteFacesReleased ? (d(e.faces), null) : (E._nativeRouteFaces.push(...e.faces), e), () => null) : null;
				if (C._mode === "main" && C._document?.embeddedFonts?.length) {
					let e = C, t = await _t(C._document, (t) => e.getFontBytes(t));
					if (c?.aborted) throw o(t.faces), new N();
					R(C, t.diagnostics), C._embeddedFontFaces = t.faces, r = t.metrics, w = t.routes;
				}
				let O = C._mode === "main" && C._document ? await it(Re(C._document, {
					fontDemand: !!a.fonts,
					cjkFallback: u
				}).filter((e) => e.presenceOnly || !w?.some((t) => t.requestedFamily.toLowerCase() === e.family.toLowerCase() && t.weight === (e.weight ?? 400) && t.style === (e.style ?? "normal")))) : {
					faces: [],
					routes: {}
				};
				if (c?.aborted) throw d(O.faces), new N();
				C._officeFontFaces = O.faces;
				let { installedSubstituteFamilies: ee, sourceFonts: k } = await C._loadFontSources(j(a.fonts), u, O, c), A;
				if (C._mode === "main" && a.math && C._document && He(C._document) && (A = await We(C._document, a.math)), l(), C._mode === "main" && C._document && C._source) {
					let e = C, t = b(C), n = {
						allowFootnoteContinuation: C._allowFootnoteContinuation,
						fontMetrics: r,
						fontSubstitutes: x(j(a.fonts)),
						cjkFallback: u,
						embeddedRoutes: w,
						officeRoutes: Object.values(O.routes),
						sourceFonts: k,
						installedSubstituteFamilies: ee,
						installedFamilies: "installed" in O ? O.installed : void 0,
						mathResources: A?.records,
						mathDrawables: A?.drawables
					}, o = await D;
					l();
					let f = new AbortController(), p = () => f.abort();
					c?.addEventListener("abort", p, { once: !0 }), C._servedFaceProbe = f;
					let m;
					try {
						m = await S(k?.loaded, i(), Me(C._source), void 0, f.signal);
					} finally {
						c?.removeEventListener("abort", p), C._servedFaceProbe === f && (C._servedFaceProbe = null);
					}
					if (c?.aborted || C._nativeRouteFacesReleased) throw d(m.faces), new N();
					C._nativeRouteFaces.push(...m.faces), t.services = Be(C._source, {
						...n,
						servedFaceLines: m,
						nativeRouteMetrics: o && o.faces.length > 0 ? Ue(o.lines, i()) : void 0
					});
					let h = t.services, g = Fe(C._source, h, t.defaultCurrentDateMs), _ = C._source.fatalParse === null, v = t.activeLayoutOptions;
					if (!v) throw Error("Active layout view was not recorded at load");
					let y = { onProgress: a.onLayoutProgress ? (t) => e._layoutObservers.notify("onLayoutProgress", a.onLayoutProgress, { committedUnits: t }) : void 0 };
					if (_ && a.progressiveLayout) {
						let e = g.layoutVariants, t = C, n = new AbortController();
						t._layoutAbort = n;
						let r = je(), i = null, o = !0;
						t._layoutCompletion = Ut(C._source.bodyLayoutInput, h, v, {
							scheduler: {
								...y,
								signal: n.signal
							},
							onPreview: (n) => {
								if (!o) return;
								let s = i === null, c = Gt(i?.pages, n.layout.pages), l = t._replaceMainLayoutPublication(e, v, i, n.layout);
								if (l === null) {
									o = !1;
									return;
								}
								if (i = l, s) t._layoutLifecycle.begin(), q(t, {
									pageCount: n.layout.pages.length,
									exact: n.exact,
									complete: !1
								}), r.resolve();
								else {
									if (!t._isLayoutViewActive(v)) return;
									q(t, {
										pageCount: n.layout.pages.length,
										exact: n.exact,
										complete: !1,
										unchangedPages: c
									}), t._layoutObservers.notify("onLayoutPartial", a.onLayoutPartial, {
										availableUnits: n.layout.pages.length,
										exact: n.exact
									});
								}
							}
						}).then((n) => {
							let s;
							o && (s = Gt(i?.pages, n.pages), t._replaceMainLayoutPublication(e, v, i, n) === null && (o = !1)), t._layoutLifecycle.succeed(), q(t, {
								pageCount: t.pageCount,
								exact: !0,
								complete: !0,
								...o && t._isLayoutViewActive(v) && s !== void 0 ? { unchangedPages: s } : {}
							}), t._layoutObservers.notify("onLayoutComplete", a.onLayoutComplete), r.resolve();
						}).catch((e) => {
							if (i === null) {
								r.reject(e);
								return;
							}
							if (e instanceof N) {
								t._layoutLifecycle.succeed();
								return;
							}
							let n = t._layoutLifecycle.fail(e);
							q(t, {
								pageCount: t.pageCount,
								exact: !1,
								complete: !1,
								error: n
							}), t._layoutObservers.notify("onLayoutComplete", a.onLayoutComplete, n);
						}), await r.promise;
					} else if (_ && (a.sliceLayout !== !1 || a.onLayoutProgress)) for (;;) {
						l();
						let e = s?.requestedView(), n = e === void 0 ? v : M(a.currentDate, t.defaultCurrentDateMs, e);
						t.activeLayoutOptions = n;
						let r = new AbortController(), i = !1, o = s?.subscribeViewChange(() => {
							let e = s.requestedView();
							i || e === void 0 || e === !0 == (n.showTrackedChanges === !0) || (i = !0, r.abort());
						});
						C._layoutAbort = r;
						try {
							let e = await ze(C._source.bodyLayoutInput, h, n, {
								...y,
								signal: r.signal
							});
							if (l(), i) continue;
							g.layoutVariants.prime(n, e);
							break;
						} catch (e) {
							if (e instanceof N && i && !c?.aborted) continue;
							throw e;
						} finally {
							o?.(), C._layoutAbort = null;
						}
					}
					else g.layoutVariants.layoutFor(v);
				}
				return l(), await C._resourceUsage(a.workerTimeoutMs ?? 1e3).then((e) => h.observeUsage(e), () => void 0), h.checkpoint("model and layout ready"), l(), h.succeed({ pages: C.pageCount }), C;
			} catch (e) {
				throw ye(_, C ? T : void 0), e;
			} finally {
				c?.removeEventListener("abort", T);
			}
		} catch (e) {
			throw h.fail(e), e;
		}
	}
	_fontSourceLoad = null;
	_servedFaceProbe = null;
	_probeLifetime = null;
	_lifetimeSignal() {
		return (this._probeLifetime ??= new AbortController()).signal;
	}
	async _loadFontSources(e, t, n, r) {
		if (this._mode !== "main" || !e?.length || !this._document) return { installedSubstituteFamilies: [] };
		let { completeDocxFontPresence: i, docxFontFamilyPlan: a, loadDocxFontSources: o, metafileFontDemand: s } = await import("./font-source-load-DtHoLLYl.js");
		if (r?.aborted || !this._document) throw new N();
		let c = await i(this._document, e, t, n);
		if (r?.aborted || !this._document) throw new N();
		let l = a(this._document, e, t, c), u = new AbortController();
		this._fontSourceLoad = u;
		let d;
		try {
			d = await o(this._document, l, e, { signal: u.signal });
		} catch (e) {
			throw u.signal.aborted || r?.aborted ? new N() : e;
		} finally {
			this._fontSourceLoad === u && (this._fontSourceLoad = null);
		}
		if (u.signal.aborted || r?.aborted) throw d.session.release(), new N();
		return this._fontSourceSession = d.session, this._chartFontSubstitutions = xe(d.loaded), oe(this._fetchImage, d.loaded), ae(this._fetchImage, s(d.session)), {
			installedSubstituteFamilies: l.installedSubstituteFamilies,
			sourceFonts: {
				names: d.names,
				loaded: d.loaded,
				lineMetrics: d.lineMetrics
			}
		};
	}
	_attachFontResolverBridge(e) {
		this._fontResolverBridge?.dispose(), this._fontResolverBridge = new le({
			post: (e, t) => this._worker.postMessage(e, t),
			sources: e
		});
	}
	async _parse(e, t, n = void 0, r, i, a, o) {
		if (this._mode === "worker" && this._attachFontResolverBridge(n), o) {
			await this._parseProgressively(e, t, n, r, i, a, o);
			return;
		}
		let s = await this._bridge.request((r) => (this._parseRequestId = r, this._mode === "worker" ? {
			type: "parse",
			id: r,
			data: e,
			resourcePolicy: t,
			...n ? { fonts: n } : {},
			allowFootnoteContinuation: this._allowFootnoteContinuation,
			cjkFallback: this._cjkFallback,
			defaultCurrentDateMs: b(this).defaultCurrentDateMs,
			...this._parseViewFields(),
			renderers: a
		} : {
			type: "parse",
			id: r,
			data: e,
			resourcePolicy: t
		}), [e], { timeoutMs: r });
		if (this._parseRequestId = null, "protocol" in s) throw Error("DOCX parse open returned a pull-protocol response");
		if (this._mode === "worker") if ("usage" in s && s.usage && i?.(s.usage), s.type === "mainThreadVerticalFallback") {
			let e = await P(this._bridge.transport(F), s, {
				timeoutMs: r,
				onUsage: i,
				lifetime: () => this._lifetimeSignal()
			});
			this._source = e.source, this._document = e.document, this._meta = null, this._mode = "main", this._mainThreadFallbackReason = s.reason ?? "vertical";
		} else this._meta = s.meta;
		else {
			let e = s, t = await P(this._bridge.transport(F), e, {
				timeoutMs: r,
				onUsage: i,
				lifetime: () => this._lifetimeSignal()
			});
			this._source = t.source, this._document = t.document;
		}
		this._review = $(this._meta?.comments ?? this._document?.comments ?? [], this._meta?.revisions ?? this._document?.revisions ?? []);
	}
	_onWorkerLayoutPush(e) {
		if (this._fontResolverBridge?.accept(e) || fe((e, t) => this._worker.postMessage(e, t), e) || !("forId" in e) || e.forId !== this._parseRequestId) return;
		if (this._rearmParseWatchdog(), e.type === "measureHostFontLines") {
			et(e.routes).catch(() => []).then((t) => {
				e.forId === this._parseRequestId && this._worker.postMessage({
					type: "hostFontLinesMeasured",
					forId: e.forId,
					measurements: t
				});
			});
			return;
		}
		if (e.type === "measureServedFaceLines") {
			w(e.requests, (this._probeLifetime ??= new AbortController()).signal).catch(() => []).then((t) => {
				e.forId === this._parseRequestId && this._worker.postMessage({
					type: "servedFaceLinesMeasured",
					forId: e.forId,
					measurements: t
				});
			});
			return;
		}
		if (e.type === "measureNativeRouteLines") {
			Ve(e.requests, !1).then((e) => e.lines, () => e.requests.map(() => null)).then((t) => {
				e.forId === this._parseRequestId && this._worker.postMessage({
					type: "nativeRouteLinesMeasured",
					forId: e.forId,
					lines: t
				});
			});
			return;
		}
		let t = this._progressive;
		if (t?.settled) return;
		if (e.type === "layoutProgress") {
			this._layoutObservers.notify("onLayoutProgress", t?.onProgress, { committedUnits: e.committedPages });
			return;
		}
		if (e.type !== "layoutPartial" || !t) return;
		let n = !t.published || this._isLayoutViewActive(t.layoutOptions);
		if (n && this._applyLayoutPartial(e.partial), t.published) {
			if (!n) return;
			q(this, {
				pageCount: e.partial.pageCount,
				exact: e.partial.exact,
				complete: !1,
				...e.partial.unchangedPages === void 0 ? {} : { unchangedPages: e.partial.unchangedPages }
			}), this._layoutObservers.notify("onLayoutPartial", t.onPartial, {
				availableUnits: e.partial.pageCount,
				exact: e.partial.exact
			});
			return;
		}
		t.published = !0, this._layoutLifecycle.begin(), q(this, {
			pageCount: e.partial.pageCount,
			exact: e.partial.exact,
			complete: !1
		}), t.firstPublication.resolve();
	}
	_applyLayoutPartial(e) {
		let t = e.review ?? this._meta;
		this._meta = {
			pageCount: e.pageCount,
			pageSizes: e.pageSizes,
			bookmarkPages: e.bookmarkPages,
			revisions: t?.revisions ?? [],
			comments: t?.comments ?? [],
			footnotes: t?.footnotes ?? [],
			endnotes: t?.endnotes ?? [],
			diagnostics: e.diagnostics,
			resourceDiagnostics: e.review?.resourceDiagnostics ?? this._meta?.resourceDiagnostics,
			commentAnchorRanges: e.commentAnchorRanges,
			revisionAnchorRanges: e.revisionAnchorRanges
		}, e.review && (this._review = $(e.review.comments, e.review.revisions)), this._invalidateLayoutDerivedCaches();
	}
	_onAuthoritativeMeta(e, t) {
		this._clearParseWatchdog();
		let n = this._progressive;
		if (n?.settled) return;
		let r = n !== null && this._meta !== null && this._isLayoutViewActive(n.layoutOptions);
		if (!n || this._isLayoutViewActive(n.layoutOptions) || !this._meta) this._meta = e;
		else {
			let t = this._meta;
			this._meta = {
				...e,
				diagnostics: t.diagnostics,
				pageCount: t.pageCount,
				pageSizes: t.pageSizes,
				bookmarkPages: t.bookmarkPages,
				commentAnchorRanges: t.commentAnchorRanges,
				revisionAnchorRanges: t.revisionAnchorRanges
			};
		}
		this._invalidateLayoutDerivedCaches(), this._review = $(e.comments, e.revisions), n && (n.settled = !0, this._layoutLifecycle.succeed(), q(this, {
			pageCount: this.pageCount,
			exact: !0,
			complete: !0,
			...r && t !== void 0 ? { unchangedPages: t } : {}
		}), n.firstPublication.resolve(), this._layoutObservers.notify("onLayoutComplete", n.onComplete));
	}
	_invalidateLayoutDerivedCaches() {
		this._bookmarkPages = null, this._commentAnchorRanges = null, this._revisionAnchorRanges = null, this._reviewProjectionIndex = null;
	}
	_replaceMainLayoutPublication(e, t, n, r) {
		let i = e.replaceIfCurrent(t, n, r);
		return i !== null && this._isLayoutViewActive(t) && this._invalidateLayoutDerivedCaches(), i;
	}
	_isLayoutViewActive(e) {
		return tn(b(this).activeLayoutOptions, e);
	}
	_rearmParseWatchdog() {
		this._parseWatchdogMs !== void 0 && (clearTimeout(this._parseWatchdog), this._parseWatchdog = setTimeout(() => this._onParseWentSilent(), this._parseWatchdogMs));
	}
	_clearParseWatchdog() {
		clearTimeout(this._parseWatchdog), this._parseWatchdog = void 0, this._parseWatchdogMs = void 0;
	}
	_onParseWentSilent() {
		let e = this._progressive, t = this._parseWatchdogMs;
		this._clearParseWatchdog();
		let n = /* @__PURE__ */ Error(`worker layout produced no progress for ${t}ms`);
		e && this._failWorkerProgressive(e, n), this._bridge.terminate();
	}
	_failWorkerProgressive(e, t) {
		if (e.settled) return;
		if (e.settled = !0, this._clearParseWatchdog(), !e.published) {
			e.firstPublication.reject(t);
			return;
		}
		let n = this._layoutLifecycle.fail(t);
		q(this, {
			pageCount: this.pageCount,
			exact: !1,
			complete: !1,
			error: n
		}), this._layoutObservers.notify("onLayoutComplete", e.onComplete, n);
	}
	_parseViewFields() {
		let e = b(this), t = e.activeLayoutOptions;
		return t ? {
			...t.currentDateMs === e.defaultCurrentDateMs ? {} : { currentDateMs: t.currentDateMs },
			...t.showTrackedChanges === !0 ? { showTrackedChanges: !0 } : {}
		} : {};
	}
	async _parseProgressively(e, t, n, r, i, a, o) {
		this._progressive = o, this._layoutAbort = o.abort, this._parseWatchdogMs = r;
		let s = this._bridge.request((r) => (this._parseRequestId = r, {
			type: "parse",
			id: r,
			data: e,
			resourcePolicy: t,
			...n ? { fonts: n } : {},
			allowFootnoteContinuation: this._allowFootnoteContinuation,
			cjkFallback: this._cjkFallback,
			defaultCurrentDateMs: b(this).defaultCurrentDateMs,
			...this._parseViewFields(),
			renderers: a,
			progressiveLayout: !0
		}), [e], { timeoutMs: !1 });
		this._layoutCompletion = s.then(async (e) => {
			if (this._parseRequestId = null, "protocol" in e) throw Error("DOCX parse open returned a pull-protocol response");
			if ("usage" in e && e.usage && i?.(e.usage), e.type === "mainThreadVerticalFallback") {
				this._clearParseWatchdog(), o.settled = !0, this._progressive = null, this._layoutAbort = null;
				let t = await P(this._bridge.transport(F), e, {
					timeoutMs: r,
					onUsage: i,
					lifetime: () => this._lifetimeSignal()
				});
				this._source = t.source, this._document = t.document, this._meta = null, this._mode = "main", this._mainThreadFallbackReason = e.reason ?? "vertical", this._review = $(t.document.comments ?? [], t.document.revisions ?? []), o.firstPublication.resolve();
				return;
			}
			let t = e;
			this._onAuthoritativeMeta(t.meta, t.unchangedPages);
		}, (e) => {
			if (this._parseRequestId = null, this._clearParseWatchdog(), !o.settled) {
				if (o.abort.signal.aborted) {
					o.settled = !0, this._layoutLifecycle.succeed(), o.firstPublication.resolve();
					return;
				}
				this._failWorkerProgressive(o, e);
			}
		}), this._rearmParseWatchdog(), await o.firstPublication.promise;
	}
	destroy() {
		this._layoutAbort?.abort(), this._layoutAbort = null, this._clearParseWatchdog(), this._parseRequestId = null, this._progressive = null, this._layoutViewGeneration++, this._bridge.terminate(), this._document = null, this._source = null, this._meta = null, Z(this).close(), this._review = an, b(this).services = null, this._bookmarkPages = null, this._commentAnchorRanges = null, this._revisionAnchorRanges = null, this._reviewProjectionIndex = null, this._rawParts.clear(), this._embeddedFontFaces.length > 0 && (o(this._embeddedFontFaces), this._embeddedFontFaces = []), this._officeFontFaces.length > 0 && (d(this._officeFontFaces), this._officeFontFaces = []), this._nativeRouteFacesReleased = !0, this._nativeRouteFaces?.length > 0 && (d(this._nativeRouteFaces), this._nativeRouteFaces = []), this._fontSourceLoad?.abort(), this._fontSourceLoad = null, this._servedFaceProbe?.abort(), this._servedFaceProbe = null, (this._probeLifetime ??= new AbortController()).abort(), this._fontResolverBridge?.dispose(), this._fontResolverBridge = null;
		let e = this._fontSourceSession;
		this._fontSourceSession = null, this._chartFontSubstitutions = void 0, e?.release(), re(this._fetchImage), oe(this._fetchImage, void 0), ae(this._fetchImage, void 0), ne(this._fetchImage);
	}
	async getImage(e, t) {
		return this._rawParts.get(e, t, () => this._bridge.request((t) => ({
			type: "extractImage",
			id: t,
			path: e
		})).then((e) => {
			let n = e.bytes;
			return new Blob([n], { type: t });
		}));
	}
	async getFontBytes(e) {
		let t = (await this._bridge.request((t) => ({
			type: "extractImage",
			id: t,
			path: e
		}))).bytes;
		return new Uint8Array(t);
	}
	async _resourceUsage(e) {
		return (await this._bridge.request((e) => ({
			type: "resourceUsage",
			id: e
		}), void 0, { timeoutMs: e })).usage;
	}
	async getResourceMetrics() {
		let e = this._metrics;
		if (!e) throw Error("Document not loaded");
		return ve(e, (e) => this._resourceUsage(e));
	}
	async toMarkdown() {
		return (await this._bridge.request((e) => ({
			type: "toMarkdown",
			id: e
		}))).markdown;
	}
	get pageCount() {
		return this._meta ? this._meta.pageCount : this._document ? this._getLayout()?.pages.length ?? 0 : 0;
	}
	get layoutComplete() {
		return this._layoutLifecycle.complete;
	}
	async waitUntilLayoutComplete() {
		this._layoutCompletion && await this._layoutCompletion, this._layoutLifecycle.throwIfFailed();
	}
	get mode() {
		return this._mode;
	}
	get document() {
		if (this._meta && !this._document) throw Error("the raw document model stays in the worker in mode: 'worker'; use mode: 'main' if you need direct model access");
		if (!this._document) throw Error("Document not loaded");
		return this._document;
	}
	get comments() {
		return this._reviewSnapshot().comments;
	}
	get revisions() {
		return this._reviewSnapshot().revisions;
	}
	commentAnchorRanges() {
		if (this._meta) return this._meta.commentAnchorRanges ?? nn;
		if (!this._document || !this._source) return [];
		let e = this._reviewSnapshot().comments;
		if (e.length === 0) return nn;
		let t = b(this), n = t.services;
		if (!n) throw Error("Document layout services are not initialized");
		let r = C(n);
		if (!r) throw Error("Document layout variant store is not initialized");
		let i = t.activeLayoutOptions, a = i ? r.layoutFor(i) : r.defaultLayout;
		this._reviewProjectionIndex ??= Ne(a);
		let o = this._layoutLifecycle?.complete ?? !0 ? void 0 : { completedSourceKeys: this._reviewProjectionIndex.completedSourceKeys };
		return this._commentAnchorRanges ??= Ze(e, this._source, this._reviewProjectionIndex.renderedRunIndex, o), this._commentAnchorRanges;
	}
	revisionAnchorRanges() {
		if (this._meta) return this._meta.revisionAnchorRanges ?? rn;
		if (!this._document || !this._source) return [];
		let e = this._reviewSnapshot().revisions;
		if (e.length === 0) return rn;
		let t = b(this), n = t.services;
		if (!n) throw Error("Document layout services are not initialized");
		let r = C(n);
		if (!r) throw Error("Document layout variant store is not initialized");
		let i = t.activeLayoutOptions, a = i ? r.layoutFor(i) : r.defaultLayout;
		this._reviewProjectionIndex ??= Ne(a);
		let o = this._layoutLifecycle?.complete ?? !0 ? void 0 : { completedSourceKeys: this._reviewProjectionIndex.completedSourceKeys };
		return this._revisionAnchorRanges ??= Bt(e, this._source, this._reviewProjectionIndex.renderedRunIndex, o), this._revisionAnchorRanges;
	}
	_reviewSnapshot() {
		return this._review ||= $(this._meta?.comments ?? this._document?.comments ?? [], this._meta?.revisions ?? this._document?.revisions ?? []), this._review;
	}
	get footnotes() {
		return this._meta?.footnotes ?? this._document?.footnotes ?? [];
	}
	get endnotes() {
		return this._meta?.endnotes ?? this._document?.endnotes ?? [];
	}
	_getLayout() {
		if (!this._document) return null;
		let e = b(this), t = e.services;
		if (!t) throw Error("Document layout services are not initialized");
		let n = C(t);
		if (!n) throw Error("Document layout variant store is not initialized");
		let r = e.activeLayoutOptions;
		return r ? n.layoutFor(r) : n.defaultLayout;
	}
	async setLayoutView(e = {}) {
		let t = e[qt], n = b(this), r = M(e.currentDate, n.defaultCurrentDateMs, e.showTrackedChanges === !0), i = ++this._layoutViewGeneration, a = n.activeLayoutOptions;
		if (!tn(a, r)) {
			if (this._mode === "worker" && this._meta) {
				let e = await this._bridge.request((e) => ({
					type: "selectLayoutView",
					id: e,
					currentDateMs: r.currentDateMs,
					showTrackedChanges: r.showTrackedChanges === !0
				}));
				if (i !== this._layoutViewGeneration) return;
				let a = e;
				n.activeLayoutOptions = r, this._meta = {
					...this._meta,
					...a.meta
				}, this._invalidateLayoutDerivedCaches(), Xt(this, t);
				return;
			}
			n.activeLayoutOptions = r, this._invalidateLayoutDerivedCaches(), Xt(this, t);
		}
	}
	_getBookmarkPages() {
		if (this._bookmarkPages) return this._bookmarkPages;
		if (this._meta) return this._bookmarkPages = new Map(this._meta.bookmarkPages), this._bookmarkPages;
		let e = this._getLayout();
		return e ? (this._bookmarkPages = dt(e), this._bookmarkPages) : null;
	}
	getBookmarkPage(e) {
		return this._getBookmarkPages()?.get(e);
	}
	pageSize(e) {
		if (this._meta) {
			let t = this._meta.pageSizes, n = t[Math.max(0, Math.min(e, t.length - 1))];
			return n ? {
				widthPt: n.widthPt,
				heightPt: n.heightPt
			} : {
				widthPt: 0,
				heightPt: 0
			};
		}
		if (!this._document) return {
			widthPt: 0,
			heightPt: 0
		};
		let t = this._getLayout();
		if (!t || t.pages.length === 0) return {
			widthPt: 0,
			heightPt: 0
		};
		let n = Math.max(0, Math.min(e, t.pages.length - 1)), r = t.pages[n].geometry;
		return {
			widthPt: r.widthPt,
			heightPt: r.heightPt
		};
	}
	_withActiveView(e) {
		let t = b(this).activeLayoutOptions;
		if (!t) return e;
		let n = { ...e };
		return e.currentDate === void 0 && (n.currentDate = t.currentDateMs), e.showTrackedChanges === void 0 && t.showTrackedChanges === !0 && (n.showTrackedChanges = !0), n;
	}
	renderPage(e, t, n = {}) {
		if (this._mode !== "worker" && "errorPlaceholder" in n) {
			let { errorPlaceholder: r, ...i } = n, a;
			try {
				a = this._errorPlaceholderText(r);
			} catch (e) {
				return Promise.reject(e);
			}
			return this._renderPageWithTargetOwnership(e, t, a === void 0 ? i : {
				...i,
				errorPlaceholderText: a
			}, !0);
		}
		return this._renderPageWithTargetOwnership(e, t, n, !0);
	}
	_renderPageWithTargetOwnership(e, t, n, r) {
		if (this._mode === "worker") throw Error("renderPage(canvas) is unavailable in mode: 'worker'; use renderPageToBitmap() and paint it via an ImageBitmapRenderingContext");
		if (!this._source) throw Error("Document not loaded");
		return Le(this._source, e, t, {
			...this._withActiveView(n),
			onDiagnostic: (e) => R(this, [e]),
			callerOwnedCanvasTarget: r,
			fetchImage: this._fetchImage,
			layoutServices: b(this).services ?? void 0,
			defaultCurrentDateMs: b(this).defaultCurrentDateMs,
			threeD: this._threeD,
			regionMap: this._regionMap,
			chartEx: this._chartEx,
			tiff: this._tiff,
			chartFontSubstitutions: this._chartFontSubstitutions
		});
	}
	async renderPageToBitmap(e, t = {}) {
		let { onTextRun: n, errorPlaceholder: r, ...i } = t, a = this._errorPlaceholderText(r), o = {
			...this._withActiveView(i),
			dpr: i.dpr ?? A(),
			...a === void 0 ? {} : { errorPlaceholderText: a }
		};
		if (this._mode === "worker") {
			let t = new OffscreenCanvas(1, 1), r = await this._bridge.request((n) => ({
				type: "renderPage",
				id: n,
				pageIndex: e,
				opts: o,
				canvas: t
			}), [t]);
			try {
				if (R(this, r.diagnostics), n) for (let e of r.runs) n(e);
			} catch (e) {
				throw ie(r.bitmap), e;
			}
			return r.bitmap;
		}
		let s = new OffscreenCanvas(1, 1);
		return await this._renderPageWithTargetOwnership(s, e, {
			...o,
			onTextRun: n
		}, !1), s.transferToImageBitmap();
	}
	async collectPageRuns(e, t = {}) {
		let n = this._withActiveView({
			...t.width === void 0 ? {} : { width: t.width },
			...t.currentDate === void 0 ? {} : { currentDate: t.currentDate },
			...t.showTrackedChanges === void 0 ? {} : { showTrackedChanges: t.showTrackedChanges }
		});
		if (this._mode === "worker") return (await this._bridge.request((t) => ({
			type: "collectRuns",
			id: t,
			pageIndex: e,
			opts: n
		}))).runs;
		let r = b(this), i = r.services;
		if (!i) throw Error("Document layout services are not initialized");
		return Ie(i, e, {
			currentDate: n.currentDate,
			defaultCurrentDateMs: r.defaultCurrentDateMs,
			width: n.width,
			showTrackedChanges: n.showTrackedChanges
		});
	}
	async getCommentThreads(e, t = {}) {
		let { includeResolved: n, ...r } = t, i = await this.collectPageRuns(e, r);
		return Xe(this.comments, this.commentAnchorRanges(), i, { includeResolved: n });
	}
	async getElementContextAt(e, t, n = {}) {
		let r = this._withActiveView({
			...n.maxTextCharacters === void 0 ? {} : { maxTextCharacters: n.maxTextCharacters },
			...n.currentDate === void 0 ? {} : { currentDate: n.currentDate },
			...n.showTrackedChanges === void 0 ? {} : { showTrackedChanges: n.showTrackedChanges }
		});
		if (this._mode === "worker") return (await this._bridge.request((n) => ({
			type: "hitTestElement",
			id: n,
			pageIndex: e,
			point: t,
			opts: r
		}))).context;
		let i = b(this), a = i.services;
		if (!a) throw Error("Document layout services are not initialized");
		return Pt(a, e, t, {
			...r,
			defaultCurrentDateMs: i.defaultCurrentDateMs
		});
	}
};
export { R as _, X as a, Zt as c, Ut as d, Vt as f, ut as g, _t as h, $t as i, q as l, Ft as m, en as n, Yt as o, bt as p, Q as r, Jt as s, on as t, Wt as u, it as v };
