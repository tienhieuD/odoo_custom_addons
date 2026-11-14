# Changelog

## 18.0.1.0.2 (2026-11-14) - Vary: Accept on /web/image
- Behaviour: responses of ir.binary image streams now carry `Vary: Accept` (WebP or original depends on the Accept header), so browser/CDN caches no longer reuse the wrong format.
- Code: `models/ir_binary.py` adds the header through `request.future_response` (skipped when there is no real request).
- Test: `TestWebpHttp.test_vary_accept_header` (red before, green after). No field/view/migration change.
