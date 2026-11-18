var e = "" + new URL("./assets/render-worker-DZt08DB-.js", import.meta.url).href;
function t() {
	return new Worker(e, { type: "module" });
}
export { t as createRenderWorker };
