# Changelog

## 13.0.1.0.2 (2026-11-14) - Vary: Accept on /web/image
- Behaviour: `/web/image` responses now carry `Vary: Accept` (WebP or the original depends on the Accept header), so browser/CDN caches no longer reuse the wrong format.
- Code: `controllers/main.py` (`WebpBinary.content_image`) adds the header to the response it returns, also when the conversion is skipped or falls back.
- Test: `TestWebpHttp.test_vary_accept_header` (red before, green after). No field/view/migration change.
