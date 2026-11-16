var e = "" + new URL("./assets/render-worker-j1PT6zsz.js", import.meta.url).href;
function t() {
	return new Worker(e, { type: "module" });
}
export { t as createRenderWorker };
