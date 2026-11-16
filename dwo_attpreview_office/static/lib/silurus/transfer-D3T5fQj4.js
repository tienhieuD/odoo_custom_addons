function e(e) {
	return e.byteOffset === 0 && e.byteLength === e.buffer.byteLength && e.buffer instanceof ArrayBuffer ? e.buffer : e.slice().buffer;
}
export { e as t };
