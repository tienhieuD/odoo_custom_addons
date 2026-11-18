# Changelog - dwo_login_themes

## 2026-11-18 - 1.0.1 (Odoo 17, 18, 19, 20)

Issue #96.

- **New option "Hide Powered by Odoo"** (Settings > Login Page Themes, `dwo_login.hide_brand`, off by default). The
  layout puts `data-dwo-hidebrand="1"` on the login container; `static/src/js/login_theme.js` then adds the class
  `dwo_brand_off` (CSS `display: none`) to `.o_brand_promotion` and to the odoo.com "Powered by" link, on DOM ready and
  from a small MutationObserver. No template is replaced and no node is removed, so it does not conflict with other
  debranding modules; if the link is already gone nothing happens. Works with the theme switched off too.
- Tests: flag emitted or not (HttpCase) and two tours (the link gets the class when on, stays when off).
- Listing: a before / after image (brand kit: photo, colours, logo, then the themed login page), text that says that the
  layout, colours and background picture are the user's own choice, and the new option.

## 2026-11-18 - 1.0.0 (Odoo 17, 18, 19, 20)

First release. Issue #96.

- **What it does:** changes only the look of the standard login page. The form, the buttons and every other sign-in option
  (reset password, sign up, OAuth, passkey, two-factor, database selector, fields added by other modules) are Odoo's own
  and are not replaced. Pages that use `web.login_layout` (reset password, sign up) get the same look.
- **How:** inherits `web.login_layout` with CSS classes (`.dwo_lc.dwo_l_<layout>` on the container), an inline
  `<style>` with CSS variables, a fixed background layer and optional intro panel, welcome text and footer text. One SCSS
  mixin per layout in `static/src/scss/login_theme.scss`. Plain-JavaScript helper `static/src/js/login_theme.js` only for
  the announcement close button, the tab title and icon, and a show/hide password button (added only when Odoo's page has none).
- **Settings:** Settings > Login Page Themes (system administrators). Stored as `ir.config_parameter` `dwo_login.*`
  (global, not per company), read and written by `res.config.settings.get_values/set_values` of the module (a False boolean
  is stored as "0"). Uploaded images (background, logo, tab icon) are `ir.attachment` records (`res_model=dwo.login.theme`)
  whose id is kept in `dwo_login.bg_att`, `logo_att`, `favicon_att`.
- **Layouts (14):** card, split_left, split_right, split_narrow, column_left, column_right, glass, gradient, minimal, dark,
  topbar, corner, intro, material. The preview tiles in Settings are pure CSS (`settings.scss`, generated).
- **Colours:** main, button, text and card colour, dark overlay (0-90 %), blur (0-20 px), 8 presets (onchange fills the colours).
- **Backgrounds:** 20 bundled WebP images made by DuoTEK (each under 150 KB, see `CREDITS`), your own image, solid colour,
  gradient. Rotation: random at each visit, one per day, by time of day (server clock, time zone of the main company), slideshow.
- **Announcement:** HTML typed by the administrator, sanitized when saved and again at each render (`tools.sanitize_notice`:
  whitelist p br b strong i em u ul ol li a h1-h4 span div hr; links http, https and mailto only with
  `rel="noopener noreferrer" target="_blank"`; no script, style, iframe, form, image, `on*`, `javascript:`). Kind, position,
  close button (remembered in the browser, keyed by a hash of the text), start and end dates.
- **Route:** `GET /dwo_login/img/<kind>/<id>` (auth none) serves only the attachment whose id is stored in the settings for
  that kind and that was made by the module; anything else is 404.
- **Uploads:** JPEG, PNG or WebP only (no SVG), up to 6 MB and 36 megapixels, decoded and recompressed with Pillow
  (WebP, at most 1920 px for backgrounds, 800x400 for logos; PNG 128 px for the tab icon).
- **Website app:** when Website is installed Odoo draws the login page inside the layout of Website, which replaces the
  standard layout: the module leaves that page alone (no theme) but the announcement is still shown (it is drawn from `web.login`).
- **Tests:** `tests/test_notice.py` (sanitizer), `tests/test_login_page.py` (anonymous GET /web/login: layouts, announcement,
  positions, dates, tampered parameter, CSS injection, backgrounds, bundled images), `tests/test_images.py` (upload rules,
  route, replace and remove, settings round trip, presets), `tests/test_tour.py` (tour `dwo_login_themes_tour`: signs in
  through the themed page with 6 layouts). Also run with `auth_signup,auth_oauth,auth_totp` and with `website` installed.
- **Port notes:** one code base for 17, 18, 19 and 20; the tour file and the 20 logo block differ slightly (see the manifest versions).
